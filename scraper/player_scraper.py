from urllib.parse import urlparse
from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *


class PlayerScraper:
    def __init__(self,
                 base_url: str = BASE_URL,
                 region: list = REGION_KEYWRORD):
        self.region = region
        self.player = get_url(get_item(base_url), "portal:player")
        self.team = set()
    
    def get_team(self, soup):
        logging.info("Running get_team method of Team Scraper class.")
        try:
            content = get_item(soup, ".teamcard.toggle-area")
            logging.info(f"Found {len(content)} items for team.")
            for box in content:
                for center in get_item(box, "center", exact=True):
                    # print(center)
                    team = get_element(center, "title")
                    if not team:
                        team = get_text(center)
                    # print(team_name)
                    logging.info(f"Found text: {team}.")
                    self.team.update(team)
        
        except Exception as e:
            logging.error(f"Error occur while executing get_team method: {e}")
            print("Error occur while executing get_team method")
    
    def get_region(self) -> list:
        logging.info("Running get_region method of Player Scraper Class")
        processed = set()
        queue = list(self.player)
        try:
            result = []
            for current_url in queue:
                logging.info(f"Scraping URL: {current_url}.")
                if current_url in processed:
                    logging.info(f"Already scrape URL: {current_url}")
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                urls = get_url(soup, "")
                logging.info(f"Found {len(urls)} items for tier.")
                for url in urls:
                    if "team" in url:
                        continue
                    parse = urlparse(url).path.replace("_", " ").lower()
                    if any(r.lower() in parse.replace("/", " ") for r in self.region):
                        logging.info(f"Get URL: {url}")
                        result.append([parse._replace("_", " "), url])
                
                processed.add(current_url)
            save_json(result, "player_region")
            logging.info("get_region method completed.")
            return result
        
        except Exception as e:
            logging.error(f"Error occur while executing get_region method: {e}.")
            print("Error occur while executing get_region method")
    
    def get_player(self, url):
        logging.info("Running get_player method of Player Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (list, set)) else [url]
        try:
            result = []
            for current_url in queue:
                logging.info(f"Scraping URL: {current_url}.")
                if current_url in processed:
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                content = get_item(soup, ".wikitable.collapsible.smwtable")
                logging.info(f"Found {len(content)} items for table.")
                for table in content:
                    player = get_item(table, ".name")
                    logging.info(f"Found {len(name)} items for name.")
                    for name in player:
                        if any(re.search(f"bg", c, re.IGNORECASE) for c in name.find_parent("tr").get("class", [])):
                            continue
                        sibling = name.find_parent("td").find_next_siblings("td")[1]
                        team = sibling.find("span")
                        team_name = team.get("data-highlighting-class", []) if team else []
                        logging.info(f"Found player team: {team_name}")
                        if any(t in team_name for t in list(self.team)):
                            player_url = name.find("a").get("href")
                            logging.info(f"Found player URL: {player_url}")
                            result.append(player_url)
            
            logging.info("get_player method completed.")
            return result
        
        except Exception as e:
            logging.error(f"Error occur while executing get_player method: {e}.")
            print("Error occur while executing get_player method")
    
    def get_player_detail(self, url):
        logging.info("Running get_player_detail method of Player Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (list, set)) else [url]
        try:
            return
        
        except Exception as e:
            logging.error(f"Error occur while executing get_player_detail method: {e}.")
            print("Error occur while executing get_player_detail method")
    
    def scrape_team(self, url):
        logging.info("Running scrape_team method of Team Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            team_roster = set()
            for item in queue:
                logging.info(f"Found item: {item}")
                current_url = item[2]
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup fetched, extracting items...")
                roster = self.get_player(soup)
                team_roster.update(roster)
                processed.add(current_url)
                
            logging.info("scrape_team method completed.")
            return list(team_roster)
        
        except Exception as e:
            logging.error(f"Error occur while executing scrape_team: {e}")
            print("Error occur while executing scrape_team")
    
    def run(self, url):
        logging.info("Running run method of Team Scraper class.")
        scrape_team = self.scrape_team(url)
        save_csv(pd.DataFrame(scrape_team), "team_roster")
        logging.info("run method completed")