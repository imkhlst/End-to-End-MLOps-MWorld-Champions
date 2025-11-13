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
        
    def scrape_tier_page(self) -> list:
        logging.info("Running scrape_tier_page method of Tournament Scraper class.")
        processed = set()
        queue = list(self.portal)
        try:
            result = []
            for current_url in queue:
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                urls = get_url(soup, "tier")
                logging.info(f"Found {len(urls)} items for tier.")
                for url in urls:
                    parse = urlparse(url).path
                    if any(t in parse.replace("/", " ") for t in self.tier):
                        logging.info(f"Get URL: {url}")
                        result.append([parse.split("/")[-1][:6], url])
                
                processed.add(current_url)
            
            save_json(result, "tier")
            logging.info("scrape_tier_page method completed.")
            return list(result)

        except Exception as e:
            logging.error(f"Error occurs while executing scrape_tier_page method: {e}")
            print("Error occurs while executing scrape_tier_page method")
    
    def scrape_tournament_page(self, url: list) -> list:
        logging.info("Running scrape_tournament_page method of Tournament Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            result = []
            for item in queue:
                logging.info(f"Found item: {item}")
                tier = item[0]
                current_url = item[1]
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                urls = get_url(soup, "")
                logging.info(f"Found {len(urls)} items for tournament.")
                for url in urls:
                    parse = urlparse(url).path
                    if any(t in parse.replace("/", " ").lower() for t in self.tournament):
                            logging.info(f"Get URL: {url}")
                            result.append([tier, " ".join(parse.split("/")[2:]).replace("_", " "), url])
                
                processed.add(current_url)
            
            save_json(result, "tournament")
            logging.info("scrape_tournament_page method completed.")
            return list(result)

        except Exception as e:
            logging.error(f"Error occurs while executing scrape_tournament_page method: {e}")
            print("Error occurs while executing scrape_tournament_page method")
    
    def scrape_stage_page(self, url: list) -> list:
        logging.info("Running scrape_stage_page method of Tournament Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            stage = []
            for item in queue:
                logging.info(f"Found item: {item}")
                tier = item[0]
                tournament = item[1]
                current_url = item[2]
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                urls = get_url(soup, "")
                logging.info(f"Found {len(urls)} items for stage.")
                for url in urls:
                    parse = urlparse(url).path
                    if any(t in parse.replace("/", " ").lower() for t in self.stage):
                        if url.startswith(current_url) and "#" not in url:
                            logging.info(f"Get URL: {url}")
                            stage.append([tier, tournament, parse.split("/")[-1].replace("_", " "), url])
            
                processed.add(current_url)
            
            save_json(stage, "stage")
            logging.info("scrape_stage_page method completed.")
            return list(stage)
        
        except Exception as e:
            logging.error(f"Error occurs while executing scrape_stage_page method: {e}")
            print("Error occurs while executing scrape_stage_page method")
    
    def run(self):
        logging.info("Running run method of Tournament Scraper class.")
        tier = self.scrape_tier_page()
        tournament = self.scrape_tournament_page(tier)
        stage = self.scrape_stage_page(tournament)
        logging.info("run method completed.")
        return tournament, stage