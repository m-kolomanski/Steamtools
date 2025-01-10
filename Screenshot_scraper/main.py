from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests as rq
import sys, getopt, os
import re

def message(msg):
    print(f"[{time.ctime()}] {msg}")

def get_profile_url(steamid):
    return f"https://steamcommunity.com/id/{steamid}/screenshots/"

def parseArguments(args):
    optlist, args = getopt.getopt(args, 'h', ['help', 'steamid='])
    arguments = {o[0].replace("-", ""): o[1] for o in optlist}
    return arguments

def checkProfile(profile_url):
    profile_html = rq.get(profile_url).text

    if "The specified profile could not be found." in profile_html:
        print("Error: Profile not found.")
        exit()

def fetchFullProfile(driver, page_url, scroll_pause = 1):
    driver.get(page_url)
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    profile = driver.page_source
    driver.quit()

    return profile

def fetchScreenshotLinks(profile_html):
    soup = BeautifulSoup(profile_html, "html.parser")
    a_tags = soup.find_all("a")
    hrefs = [a.get("href") for a in a_tags]
    ss_links = [h for h in hrefs if "sharedfiles/filedetails" in h]

    return ss_links

def fetchContentLinks(ss_links):
    content = {}
    for h in ss_links:
        page = rq.get(h).text
        soup = BeautifulSoup(page, "html.parser")
        img_link = soup.find("img", id="ActualMedia").get("src").split("?")[0]
        game = soup.select_one("div.screenshotAppName a").text
        title = soup.select_one("div.screenshotDescription")

        if not title:
            title = ""
        else:
            title = title.text.replace('"', '')

        if game not in content.keys():
            content[game] = []

        content[game].append({
            "title": title,
            "link": img_link
        })

    return content

if __name__ == "__main__":
    message("Starting screenshot scraping script.")
    arguments = arguments = parseArguments(sys.argv[1:])

    if any([x in arguments.keys() for x in ("h", "help")]):
        print("Usage: python main.py --steamid=<steamid>")
        exit()

    if not "steamid" in arguments.keys():
        print("Error: No steamid provided. Use --steamid=<steamid>")
        exit()

    profile_url = get_profile_url(arguments["steamid"])

    profile_html = rq.get(profile_url).text
    if "The specified profile could not be found." in profile_html:
        print("Error: Profile not found.")
        exit()

    message("Profile found, setting up selenium.")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU (recommended for headless)
    chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
    chrome_options.add_argument("--disable-dev-shm-usage") 

    driver = webdriver.Chrome(options=chrome_options)

    message("Loading full profile...")
    full_profile = fetchFullProfile(driver, profile_url)

    message("Profile loaded, fetching screenshot links...")
    ss_links = fetchScreenshotLinks(full_profile)

    message(f"{len(ss_links)} screenshots found, fetching direct content links, this might take several minutes...")
    content = fetchContentLinks(ss_links)

    message(f"Fetched links for {len(content)} games, downloading...")
    download_folder = f"{arguments['steamid']}_screenshots"
    os.makedirs(download_folder, exist_ok=True)
    for game, screenshots in content.items():
        message(f"Downloading {len(screenshots)} screenshots for {game}")
        folder_name = file_name = re.sub(r'[\\/:*?"<>|]', "", game)
        os.makedirs(f"{download_folder}/{folder_name}", exist_ok=True)

        for ss in screenshots:
            img = rq.get(ss["link"]).content
            file_name = re.sub(r'[\\/:*?"<>|]', "", ss['title'])
            with open(f"{download_folder}/{folder_name}/{file_name}.png", "wb") as f:
                f.write(img)

    message("Script done.")