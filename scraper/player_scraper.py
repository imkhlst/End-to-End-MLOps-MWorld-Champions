from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *


class PlayerScraper:
    def __init__(self, role: list = ROLE_KEYWORD):
        self.role = role
    
    def get_player_detail(self, soup) -> list:
        logging.info("Running get_player_detail method of Player Scraper class.")
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
                    logging.info(f"Found player team: {team_name}")
                
                if not team_name:
                    continue
                
                tables = get_item(card, ".wikitable-bordered.list")
                logging.info(f"Found {len(tables)} tables.")
                
                for table in tables:
                    if int(get_element(table, "data-toggle-area-content")) > 2:
                        continue
                    
                    rows = get_item(table, "tr")
                    logging.info(f"Found {len(rows)} player.")
                    for row in rows:
                        player_role = None
                        player_nationality = None
                        player_name = None
                        
                        role = get_item(row, "img[title]", exact=True)
                        if role:
                            player_role = get_element(role, "title").lower()
                            if player_role and "middle" in player_role:
                                player_role = player_role.replace("middle", "mid lane")
                            
                            if not any(r in player_role for r in self.role):
                                continue
                            
                            logging.info(f"Found player role: {player_role}")
                        
                        flag = get_item(row, "span.flag a[title]", exact=True)
                        if flag:
                            player_nationality = get_element(flag, "title").lower()
                            logging.info(f"Found player nationality: {player_nationality}")
                        
                        player = get_item(row, "a[title]")
                        if player and len(player) > 1:
                            if "" in player:
                                continue
                            
                            player_name = get_element(player[-1], "title")
                            
                            if player_name:
                                player_name = re.sub(r"\(.*?\)", "", player_name)
                                player_name = re.sub(r"\.", "", player_name).strip().lower()
                            
                            if player_name and ":" in player_name:
                                player_name = player_name.split(":", 1)[1]
                                
                            if player_name and "championship" in player_name.lower() or "mlbb" in player_name.lower():
                                continue
                            
                            logging.info(f"Found player: {player_name}")
                        if not player_name:
                            continue
                        
                        logging.info(f"Player info added: {player_name, player_nationality, player_role, team_name, team_region}")
                        result.add((player_name, player_nationality, player_role, team_name, team_region))
            
            logging.info("get_player_detail method completed.")            
            return list(result)
        
        except Exception as e:
            logging.error(f"Error occur while executing get_player_detail method: {e}.")
            print("Error occur while executing get_player_detail method")
    
    def scrape_player(self, url):
        logging.info("Running scrape_player method of Player Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            all_player = set()
            for item in queue:
                logging.info(f"Found item: {item}")
                tier = item[0]
                current_url = item[2]
                logging.info(f"Scraping URL: {current_url}")
                if current_url in processed:
                    logging.info(f"Already scraping URL: {current_url}")
                    continue
                
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup fetched, extracting items...")
                player = self.get_player_detail(soup)
                all_player.update(player)
                processed.add(current_url)
                
            logging.info("scrape_team method completed.")
            return list(all_player)
        
        except Exception as e:
            logging.error(f"Error occur while executing scrape_player: {e}")
            print("Error occur while executing scrape_player")
    
    def run(self, url):
        logging.info("Running run method of Player Scraper class.")
        scrape_player = self.scrape_player(url)
        save_csv(
            dataframe = scrape_player,
            filename = "player_detail",
            columns = ["player_name", "player_nationality", "player_role", "team_name", "team_region"]
        )
        logging.info("run method completed.")