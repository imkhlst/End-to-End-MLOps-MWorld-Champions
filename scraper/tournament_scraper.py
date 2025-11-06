import json
from urllib.parse import urlparse
from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *


class TournamentScraper:
    def __init__(self,
                 base_url: str = BASE_URL,
                 tournament: list = TOURNAMENT_KEYWORDS,
                 stage: list = STAGE_KEYWORD,
                 tier: list = TOURNAMENT_TIER):
        self.tournament = tournament
        self.stage = stage
        self.tier = tier
        self.portal = next(iter(get_url(get_soup(base_url), "portal:tournament")), None)
        
    def scrape_tier_page(self) -> set:
        logging.info("Running scrape_tier_page method of Tournament Scraper class.")
        try:
            if not self.portal:
                logging.error("URL not found.")
                return set()
            soup = get_soup(self.portal)
            urls = get_url(soup, "tier")
            result = set()
            for url in urls:
                if any(t in url for t in self.tier):
                    result.add(url)
            logging.info("scrape_tier_page method completed.")
            return result

        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")
    
    def scrape_tournament_page(self, url: str) -> set:
        logging.info("Running scrape_tournament_page method of Tournament Scraper class.")
        try:
            if not url:
                logging.error("URL not found.")
                return set()
            soup = get_soup(url)
            urls = get_url(soup, "")
            result = set()
            for url in urls:
                if any(t in url.lower() for t in self.tournament):
                    result.add(url)
            logging.info("scrape_tournament_page method completed.")
            return result

        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")
    
    def scrape_stage_page(self, url: str) -> set:
        logging.info("Running scrape_stage_page method of Tournament Scraper class.")
        try:
            if not url:
                logging.error("URL not found.")
                return set()
            soup = get_soup(url)
            urls = get_url(soup, "")
            result = set()
            for url in urls:
                if any(t in url.lower() for t in self.stage):
                    result.add(url)
            logging.info("scrape_stage_page method completed.")
            return result
        
        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")      
            
if __name__ == "__main__":
    # scraper = TournamentScraper()
    # tournament_path = []
    # for name in TIER:
    #     tournament = scraper.path_search(name)
    #     filtered_tournament_path = scraper.path_filter(tournament)
    #     tournament_path.append(filtered_tournament_path)
    pass