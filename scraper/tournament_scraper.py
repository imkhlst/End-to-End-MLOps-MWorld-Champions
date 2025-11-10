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
    
    def scrape_match_detail(self, url) -> list:
        logging.info("Running scrape_match_detail method of Match Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            match_detail = []
            for item in queue:
                logging.info(f"Found item: {item}")
                tier = item[0]
                tournament = item[1]
                stage = item[2]
                current_url = item[3]
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                is_knoutout = bool(get_item(soup, ".brkts-bracket", exact=True))
                is_group_stage = bool(get_item(soup, ".brkts-matchlist", exact=True))
                logging.info(f"This tournament stage has {'Knockout and Group Stage' if is_knoutout==is_group_stage==True else 'Knoutout' if is_knoutout==True else 'Group Stage'} System.")
                    
                logging.info("Soup fetched, extracting items...")
                matches = get_item(soup, ".brkts-match-has-details")
                logging.info(f"Found {len(matches)} items for match.")
                for idx, match in enumerate(matches):
                    popup = get_item(match, ".brkts-popup", exact=True)
                    logging.info(f"Found {len(popup)} items for popup.")
                    timestamp = get_item(popup, ".timer-object.timer-object-datetime-only", exact=True)
                    logging.info(f"Found {len(timestamp)} items for timestamp.")
                    date = get_text(timestamp)
                    logging.info(f"Found text: {date}")
                    
                    teams = get_item(popup, ".name.hidden-xs")
                    logging.info(f"Found {len(teams)} items for teams.")
                    home_team = get_text(teams[0])
                    logging.info(f"Found {len(home_team)} items for home team.")
                    away_team = get_text(teams[1])
                    logging.info(f"Found {len(away_team)} items for away team.")
                    
                    games = get_item(popup, ".brkts-popup-body-game")
                    logging.info(f"Found {len(games)} items for games.")
                    for game in games:
                        duration = get_text(game)
                        logging.info(f"Found text: {duration}.")
                        map_name = game.get_text()[5:]
                        if map_name=="":
                            map_name = "Default"
                        logging.info(f"Found text: {map_name}.")
                        
                        result = get_item(game, "i", exact=True).get("class", [])
                        if "fa-check" in result:
                            status = "win"
                        else:
                            status = "loss"
                        
                        logging.info(f"Found home team status: {status}")
                        match_detail.append({
                            "date": date,
                            "home_team": home_team,
                            "away_team": away_team,
                            "duration": duration,
                            "winner": home_team if status == "win" else away_team,
                            "tier": tier,
                            "tournament": tournament,
                            "stage": stage,
                            # "bracket": bracket_name
                        })
                
                processed.add(current_url)
            logging.info("scrape_match_detail method completed.")
            return match_detail
        
        except Exception as e:
            logging.error(f"Error occurs while executing scrape_match_detail method: {e}")
            print("Error occurs while executing scrape_match_detail method")
    
    def run(self):
        logging.info("Running run method of Tournament Scraper class.")
        tier = self.scrape_tier_page()
        tournament = self.scrape_tournament_page(tier)
        stage = self.scrape_stage_page(tournament)
        match_detail = self.scrape_match_detail(stage)
        save_csv(pd.DataFrame(match_detail), "match_details")
        logging.info("run method completed.")
        return stage