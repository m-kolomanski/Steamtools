# Steam screenshots downloader
Script for quick downloading of screenshots uploaded to Steam user profile. Since Steam does not have an API available for fetching any information about screenshots, the data needs to be scraped from web pages using Selenium and BeautifulSoup.

The script will create a `{steamid}_screenshots` folder and ogranize subfolders by game.

### Run
In order to run the script:
```python
python main.py --steamid {your_steam_id}
```

The script will lookup a screenshot path for a given steam id (`https://steamcommunity.com/id/{steamid}/screenshots/`). Make sure provided steamid matches what you need for a specific user profile. This page needs to be publicly available, so make sure the profile settings are correct.