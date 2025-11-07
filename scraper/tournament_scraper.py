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
        self.portal = get_url(get_soup(base_url), "portal:tournament")
        
    def scrape_tier_page(self) -> set:
        logging.info("Running scrape_tier_page method of Tournament Scraper class.")
        processed = set()
        queue = self.portal
        start = 0
        url_count = len(queue)
        try:
            result = set()
            while queue and start < url_count:
                current_url = queue.pop()
                if current_url in processed:
                    continue
                
                soup = get_soup(current_url)
                urls = get_url(soup, "tier")
                for url in urls:
                    parse = urlparse(url).path.replace("/", " ")
                    if any(t in parse for t in self.tier):
                        result.add(url)
                
                processed.add(current_url)
                start += 1
            
            save_json(result, "tier")
            logging.info("scrape_tier_page method completed.")
            return result

        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")
    
    def scrape_tournament_page(self, url: set) -> set:
        logging.info("Running scrape_tournament_page method of Tournament Scraper class.")
        processed = set()
        queue = url
        start = 0
        url_count = len(queue)
        try:
            result = set()
            while queue and start < url_count:
                current_url = queue.pop()
                if current_url in processed:
                    continue
                
                soup = get_soup(current_url)
                urls = get_url(soup, "")
                for url in urls:
                    parse = urlparse(url).path.replace("/", " ")
                    if any(t in parse.lower() for t in self.tournament):
                        result.add(url)
                
                processed.add(current_url)
                start += 1
            
            save_json(result, "tournament")
            logging.info("scrape_tournament_page method completed.")
            return result

        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")
    
    def scrape_stage_page(self, url: set) -> set:
        logging.info("Running scrape_stage_page method of Tournament Scraper class.")
        processed = set()
        queue = url
        start = 0
        url_count = len(queue)
        try:
            result = set()
            while queue and start < url_count:
                current_url = queue.pop()
                if current_url in processed:
                    continue
                
                soup = get_soup(current_url)
                urls = get_url(soup, "")
                for url in urls:
                    parse = urlparse(url).path.replace("/", " ")
                    if any(t in parse.lower() for t in self.stage):
                        if "#" in url:
                            continue
                        if url.startswith(current_url):
                            result.add(url)
                
                processed.add(current_url)
                start += 1
            
            save_json(result, "stage")
            logging.info("scrape_stage_page method completed.")
            return result
        
        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")
    
    def run(self):
        logging.info("Running run method of Tournament Scraper class.")
        tier = self.scrape_tier_page()
        tournament = self.scrape_tournament_page(tier)
        stage = self.scrape_stage_page(tournament)
        logging.info("run method completed.")