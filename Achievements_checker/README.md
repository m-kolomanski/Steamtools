# Steam new achievements checker
Simple script for periodically checking whether there are new achievements for your games of interest.

The script is split into two parts: Checker and Mailer. The checker will download data regarding games specified in config file and check whether the number of available achievements changed since the last run of the script. The Mailer will then send an email notification if any new achievements are detected.

### Config file
You can download the config template file from the repo. Simply rename it to *config.json*, specify email adress and games of interest and you are good to go. There are some basic functionalities of creating checks (run `python ./main.py --help` to see more), but the most comfortable way of editing config is to just do it manually. You can have multiple checks with separate email adresses and games assigned.

### Appdata file
Steam API is based on internal appid. The script will check the list of games provided in config file and see whether appids of specified games were saved previously. If not, full list of available games will be downloaded and searched for provided names. Appid, along with other information about the game like name and previous achievement count will be saved for future use.

### Checker
Checker will download data regarding specific games and check the number of available achievements. This will require configuring steam API key in the config file. Then, the number of currently available achievements will be compared with the number saved in *appdata.json* file. The main purpose of the script is to periodically check if new achievements are available and notify the user, so you need to keep that file intact in order for the Checker to work correctly. Checker will return an object with entry for each created check, which will then contain a list of string denoting game and number of new achievements.

### Mailer
Mailer is configured for gmail API and requires a valid *token.json* file from google cloud platform. Configuring this is beyond the scope of this script. You are free to use any other email services provider, but this will require rewriting the Mailer class.

### Run
After configuring the above, simply run `python ./main.py` for the checker to do its thing.
