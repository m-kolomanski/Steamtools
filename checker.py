import json, os, getopt
import requests as rq

class Checker:
    def __init__(self, args):
        self.parseArguments(args)

    def runPipeline(self):
        # load config file #
        try:
            with open('config.json') as config_file:
                self.config = json.load(config_file)
        except:
            raise Exception("Error when loading config file. Please download config template from the repo. You can edit it using text editor or using commands.")
        
        # check for cached app data #
        if not os.path.exists("appdata.json"):
            with open("appdata.json", "w") as appdata_file:
                json.dump({}, appdata_file, indent=4)
        
        with open('appdata.json') as appdata_file:
            self.appdata = json.load(appdata_file)

        if (len(self.arguments) == 0):
            check_results = self.runChecks()
            return check_results

        # print help if needed #
        if any([x in self.arguments.keys() for x in ('h', 'help')]):
            self.printHelp()
            return None

        # execute general set commands if any #
        for set_command in  ("set_steam_api_key", "set_provider_email_name", "set_provider_email_key"):
            if set_command in self.arguments.keys():
                self.config['general'][set_command.replace("set_", "")] = self.arguments[set_command]
            
            self.writeConfig()
            print("General config updated.")
            return None

        # create new check #
        if "create_check" in self.arguments.keys():
            if any([x not in self.arguments.keys() for x in ('check_name', 'check_email', 'check_games')]):
                raise Exception("Error creating check, check_name, check_email and check_games must be provided.")
            
            self.createCheck(self.arguments['check_name'], self.arguments['check_email'], self.arguments['check_games'])
            return None
        
        if "remove_check" in self.arguments.keys():
            if "check_name" not in self.arguments.keys():
                raise Exception("To remove check you need to provide name.")
            
            self.removeCheck(self.arguments['check_name'])
            return None

    def printHelp(self):
        print(
            '''
    This is a simple script for checking whether the number of achievements for games of interest have changed. If no commands are provided all checks will be run.

    Available commands:
        -h, --help: Prints help information.

        Commands for setting general configuration:
        --set_steam_api_key [key]:         Sets your steam API key.
        --set_provider_email_name [email]: Sets your email provider name.
        --set_provider_email_key  [key]:   Sets your email provider key.

        Commands for managing checks:
        --create_check: Creates new check. Must provide --check_name, --check_email and --check_games.
        --remove_check: Removes existing check. Must provide --check_name.
    '''
        )

    def writeConfig(self):
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

    def parseArguments(self, args):
        optlist, args = getopt.getopt(args,
                                    'h',
                                    ['help',
                                    "set_steam_api_key=", "set_provider_email_name=", "set_provider_email_key=",
                                    "create_check", "remove_check",
                                    "check_name=", "check_email=", "check_games="])
        arguments = {o[0].replace("-", ""): o[1] for o in optlist}
        self.arguments = arguments

    def createCheck(self, name, email, games):
        if name in self.config['checks'].keys():
            raise Exception(f'Check with the name {name} already exists.')
        
        self.config['checks'][name] = {
            'email': email,
            'games': games.split(",").strip()
        }

        self.writeConfig()
        print("New check created.")

    def removeChecks(self, name):
        if name not in config['checks'].keys():
            raise Exception(f'Check with name {name} does not exist.')
        
        del self.config['checks'][name]
        
        self.writeConfig()
        print("Check removed")

    def runChecks(self):
        checks_with_new_achievements = {}

        for check in self.config['checks'].values():
            games_with_new_achievements = []
            missing_game_data = [game for game in check['games'] if game not in self.appdata.keys()]

            # check for missing appids #
            if len(missing_game_data) != 0:
                print(f"Downloading app_id for {', '.join(missing_game_data)}")

                resp = rq.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
                if resp.status_code != 200:
                    print(resp)
                    raise Exception("Error downloading appdata from Steam API") 
                
                full_appdata = resp.json()['applist']['apps']
                missing_appdata = [x for x in full_appdata if x['name'] in missing_game_data]

                # check if appids for all missing games were downloaded #
                if len(missing_appdata) != len(missing_game_data):
                    fetched_names = [x['name'] for x in missing_appdata]
                    missing_names = [x for x in missing_game_data if x not in fetched_names]
                    print(f"Warning: data for the following games not found in the Steam API. Make sure the names are correct: {', '.join(missing_names)}")

                # save downloaded appdata #
                for game in missing_appdata:
                    self.appdata[game['name']] = {
                        'appid': str(game['appid']),
                        'n_achievements': None
                    }
                
                with open("appdata.json", 'w') as appdata_file:
                    json.dump(self.appdata, appdata_file, indent=4)


            # go over games and download current number of achievements #
            for game in check['games']:
                if game not in self.appdata.keys():
                    print(f"Skipping {game}")
                    continue
                
                # fetch new data from Steam API #
                resp = rq.get(f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={self.config['general']['steam_api_key']}&appid={self.appdata[game]['appid']}")

                if resp.status_code != 200:
                    print(resp)
                    print(f"Warning: failed to fetch game data for {game['name']}.")
                    continue
                
                data = resp.json()

                if 'availableGameStats' not in data['game']:
                    print(f"Warning: no game stats found for {game}")
                    n_achievements = 0
                
                elif 'achievements' not in data['game']['availableGameStats']:
                    print(f"Warning: no achievements found for {game}")
                    n_achievements = 0
                
                else:
                    n_achievements = len(data['game']['availableGameStats']['achievements'])

                if not self.appdata[game]['n_achievements']:
                    self.appdata[game]['n_achievements'] = n_achievements
                elif self.appdata[game]['n_achievements'] != n_achievements:
                    games_with_new_achievements.append(f"{game} has {n_achievements - self.appdata[game]['n_achievements']} new achievements")
                    self.appdata[game]['n_achievements'] = n_achievements

            # if any new achievements are present, send email #
            if games_with_new_achievements:
                checks_with_new_achievements[check['email']] = games_with_new_achievements

        with open('appdata.json', 'w') as appdata_file:
            json.dump(self.appdata, appdata_file, indent=4)
                
        return checks_with_new_achievements