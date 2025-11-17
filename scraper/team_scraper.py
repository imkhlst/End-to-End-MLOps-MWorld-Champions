from urllib.parse import urlparse
from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *


class TeamScraper:
    def __init__(self):
        pass
    
    def get_team_detail(self, soup) -> list:
        logging.info("Running get_team_detail method of Team Scraper class.")
        result = set()
        try:
            region = get_item(soup, ".fo-nttax-infobox", exact=True)
            cards = get_item(soup, ".teamcard.toggle-area")
            logging.info(f"Found {len(cards)} teams.")
            for card in cards:
    
                team_name = None
                team_region = None
                
                flag = get_item(region, "span.flag a[title]")
                if flag:
                    team_region = get_element(flag[0], "title")
                    logging.info(f"Found team region: {team_region}")
                
                team = get_item(card, "center > a[title]", exact=True)
                if team:
                    team_name = get_element(team, "title")
                    team_name = re.sub(r"\(.*?\)", "", team_name).strip()
                    logging.info(f"Found team name: {team_name}")
                
                if not team_name:
                    continue
                                
                logging.info(f"Player info added: {team_name, team_region}")
                result.add((team_name, team_region))
            
            logging.info("get_team_detail method completed.")            
            return list(result)
        
        except Exception as e:
            logging.error(f"Error occur while executing get_player_detail method: {e}.")
            print("Error occur while executing get_player_detail method")
    
    def scrape_player(self, url):
        logging.info("Running scrape_player method of Team Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            all_team = set()
            for item in queue:
                logging.info(f"Found item: {item}")
                tier = item[0]
                if "S-Tier" in tier or any(k in tier.lower() for k in ["invitational", "snapdragon"]):
                    logging.info(f"Skipping tournament tier: {tier}")
                    continue
                
                current_url = item[2]
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup fetched, extracting items...")
                team = self.get_team_detail(soup)
                all_team.update(team)
                processed.add(current_url)
                
            logging.info("scrape_team method completed.")
            return list(all_team)
        
        except Exception as e:
            logging.error(f"Error occur while executing scrape_team: {e}")
            print("Error occur while executing scrape_team")
    
    def run(self, url):
        logging.info("Running run method of Team Scraper class.")
        scrape_player = self.scrape_player(url)
        save_csv(
            dataframe = scrape_player,
            filename = "team",
            columns = ["team_name", "team_region"]
        )
        logging.info("run method completed")