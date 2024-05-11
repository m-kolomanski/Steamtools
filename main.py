from checker import Checker
from mailer import Mailer
import sys, os, json

if __name__ == "__main__":
    if not os.path.exists("config.json"):
        print("Configration file not found. You can download a template from the repository.\nRename template file to 'config.json' to start.")
        exit()

    checker = Checker(sys.argv[1:])
    checker_res = checker.runPipeline()

    if not checker_res:
        print("Finishing, no email to send.")
        exit()

    print("Check found new achievements, emails will be sent:")
    print(checker_res)

    with open("config.json") as config_file:
        config = json.load(config_file)

    mailer = Mailer(config['general']['provider_email_adress'])

    for email, games_with_achievements in checker_res.items():
        resp = mailer.sendMessage(email, games_with_achievements)
    
    print("Script finished correctly")