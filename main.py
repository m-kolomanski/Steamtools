from checker import Checker
from mailer import Mailer
import sys
import json

if __name__ == "__main__":
    checker = Checker(sys.argv[1:])
    checker_res = checker.runPipeline()

    if not checker_res:
        print("Finishing")
        exit()

    with open("config.json") as config_file:
        config = json.load(config_file)

    mailer = Mailer(config['general']['provider_email_name'])


    for email, games_with_achievements in checker_res.items():
        resp = mailer.sendMessage(email, games_with_achievements)