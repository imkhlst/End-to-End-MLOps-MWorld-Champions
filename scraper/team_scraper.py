from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *


class TeamScraper:
    def __init__(self):
        pass
    # need updated
    def get_team_detail(self, soup, team) -> list:
        logging.info("Running get_team_detail method of Team Scraper class.")
        all_team = list(team)
        result = set()
        try:
            region = get_item(soup, ".fo-nttax-infobox", exact=True)
            cards = get_item(soup, ".teamcard.toggle-area.toggle-area-1")
            if not cards:
                cards = get_item(soup, ".team-participant-card__opponent-compact")
            logging.info(f"Found {len(cards)} teams.")
            for card in cards:
    
                team_name = None
                team_region = None
                
                content = get_item(card, "center a[href]")
                if not content:
                    content = get_item(card, "span.name a[href]")
                
                href = content[-1].get("href")
                if "index" in href:
                    team_name = get_element(content[-1], "title")
                    team_name = re.sub(r"\(.*?\)", "", team_name).strip()
                    logging.info(f"Found team name: {team_name}")
                    if any(team_name in [t,_] for [t,_] in all_team):
                        logging.info(f"{team_name} already exists.")
                        continue
                    flag = get_item(region, "span.flag a[title]")
                    if flag:
                        team_region = get_element(flag[0], "title")
                        logging.info(f"Found team region: {team_region}")
                        logging.info(f"Team info added: {team_name, team_region}")
                        result.add((team_name, team_region))
                        continue
                
                team_url = absolute(href)
                team_soup = get_soup(team_url)
                team_content = get_item(team_soup, "h1.firstHeading", exact=True)
                team_name = get_text(team_content)
                team_name = re.sub(r"\(.*?\)", "", team_name).strip()
                if any(team_name in [t,_] for [t,_] in all_team):
                    logging.info(f"{team_name} already exist.")
                    continue
                
                logging.info(f"Found team name: {team_name}")
                infobox = get_item(team_soup, ".fo-nttax-infobox", exact=True)
                if infobox:
                    info = get_item(infobox, ".infobox-description")
                    text = []
                    for i in info:
                        text_info = get_text(i)
                        text.append(text_info)
                    
                    flag = get_item(infobox, "span.flag a[title]")
                    if any("region" or "location" in t.lower() for t in text):
                        team_region = get_element(flag[-1], "title")
                        if "asia" in team_region.lower() or "europe" in team_region.lower():
                            team_region = get_element(flag[0], "title")
                        logging.info(f"Found team region: {team_region}")
                        logging.info(f"Team info added: {team_name, team_region}")
                        result.add((team_name, team_region))
                    
                    else:
                        team_region = get_element(region[0], "title")
                        logging.info(f"Found team region: {team_region}")
                        logging.info(f"Team info added: {team_name, team_region}")
                        result.add((team_name, team_region))
                
                # flag = get_item(region, "span.flag a[title]")
                # if flag:
                #     team_region = get_element(flag[0], "title")
                #     logging.info(f"Found team region: {team_region}")
                
                # team = get_item(card, "center > a", exact=True)
                # if card:
                #     team = card.select_one("span.name a")
                # team_name = get_text(team)
                # logging.info(f"Found team name: {team_name}")
                
                # if not team_name:
                #     continue
                                
                # logging.info(f"Player info added: {team_name, team_region}")
                # result.add((team_name, team_region))
            
            logging.info("get_team_detail method completed.")            
            return list(result)
        
        except Exception as e:
            logging.error(f"Error occur while executing get_team_detail method: {e}.")
            print("Error occur while executing get_team_detail method")
    
    def scrape_team(self, url):
        logging.info("Running scrape_player method of Team Scraper class.")
        processed = set()
        queue = list(url) if isinstance(url, (set, list)) else [url]
        print(f"Queue: {queue[:3]}")
        try:
            all_team = list()
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
                team = self.get_team_detail(soup, all_team)
                all_team.extend(team)
                processed.add(current_url)
                
            logging.info("scrape_team method completed.")
            return list(all_team)
        
        except Exception as e:
            logging.error(f"Error occur while executing scrape_team: {e}")
            print("Error occur while executing scrape_team")
    
    def run(self, url):
        logging.info("Running run method of Team Scraper class.")
        scrape_team = self.scrape_team(url)
        save_csv(
            dataframe = scrape_team,
            filename = "team_detail",
            columns = ["team_name", "team_region"]
        )
        logging.info("run method completed.")