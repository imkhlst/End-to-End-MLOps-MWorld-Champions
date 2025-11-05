import json
from urllib.parse import urlparse
from constants.scraper_constant import KEYWORDS, TIER
from logger import logging
from utils.scraper_utils import *


class TournamentScraper:
    def __init__(self, keywords: list = KEYWORDS, tier: list = TIER):
        self.keywords = KEYWORDS
        self.tier = TIER
    
    def path_search(self, url: str) -> set:
        logging.info("Running path_search method of Tournament Scraper class.")
        url_path = absolute(url)
        try:
            soup = get_soup(url_path)
            print(f"Page found: {url_path}.")
            
            content = soup.find(id="mw-content-text")
            tournament_path = set()
            if content:
                for a in content.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("/mobilelegends/") or href.startswith("/"):
                        if ":" in href:
                            continue
                        full_path = absolute(href)
                        tournament_path.add(full_path)
            logging.info("page_search method completed.")
            return tournament_path
        
        except Exception as e:
            logging.error("Error occurs while executing page_search method: {e}")
            print("Error occurs while executing page_search method")
    
    def path_filter(self, tournament_path: set, file_path: str) -> list:
        logging.info("Running path_filter method of Tournament Scraper class.")
        try:
            sorted_path = sorted(tournament_path)
            filtered_path = []
            for path in sorted_path:
                parse_path = urlparse(path).path.lower()
                keywords = self.keywords
                if any(k in parse_path for k in keywords):
                    filtered_path.append(path)
            
            with open(f"data/links/{file_path}.json", "w") as file:
                json.dump(filtered_path, file)
            logging.info("path_filter method completed.")
            return filtered_path
        
        except Exception as e:
            logging.error("Error occurs while executing page_search method: {e}")
            print("Error occurs while executing page_search method")
            
            
if __name__ == "__main__":
    # scraper = TournamentScraper()
    # tournament_path = []
    # for name in TIER:
    #     tournament = scraper.path_search(name)
    #     filtered_tournament_path = scraper.path_filter(tournament)
    #     tournament_path.append(filtered_tournament_path)
    pass