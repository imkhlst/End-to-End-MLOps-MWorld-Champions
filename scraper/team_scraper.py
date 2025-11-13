from urllib.parse import urlparse
from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *


class TeamScraper:
    def __init__(self):
        pass
    
    def get_player(self, soup):
        logging.info("Running get_player method of Team Scraper class.")
        result = set()
        try:
            content = get_item(soup, ".teamcard.toggle-area")
            logging.info(f"Found {len(content)} items for team.")
            for box in content:
                for center in get_item(box, "center", exact=True):
                    # print(center)
                    team = get_element(center, "title")
                    # print(team_name)
                    logging.info(f"Found text: {team}.")
                    for card in get_item(box, "div", exact=True):
                        if "logo" in get_element(card, "class"):
                            continue
                        # print(card)
                        
                        all_role = []
                        all_nasionality = []
                        all_name = []
                        for th in get_item(card, "th"):
                            for img in get_item(th, "img"):
                                role = get_element(img, "title")
                                logging.info(f"Found text: {role}.")
                                all_role.append(role)
                        for td in get_item(card, "span"):
                            if not "flag" in get_element(td, "class"):
                                continue
                            for a in get_item(td, "a"):
                                nasionality = get_element(a, "title")
                                logging.info(f"Found text: {nasionality}.")
                                all_nasionality.append(nasionality)
                        for a in get_item(card, "a"):
                            name = get_element(a, "title")
                            if name in all_nasionality:
                                continue
                            if "page does not exist" in name:
                                name = name[:-len("(page does not exist)")]
                            logging.info(f"Found text: {name}.")
                            all_name.append(name)
                        for name, role, nasionality in zip(all_name, all_role, all_nasionality):
                            logging.info(f"{(name, role, nasionality, team)} added.")
                            result.add((name, role, nasionality, team))
            return result
        
        except Exception as e:
            logging.error(f"Error occur while executing get_player method: {e}")
            print("Error occur while executing get_player method")
    
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