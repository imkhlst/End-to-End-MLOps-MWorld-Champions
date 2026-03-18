import warnings
from dateutil import parser
from dateutil.parser import UnknownTimezoneWarning
from constants.scraper_constant import *
from logger import logging
from utils.scraper_utils import *

warnings.filterwarnings("ignore", category=UnknownTimezoneWarning)

class MatchScraper:
    def __init__(self,
                 tournament: list = TOURNAMENT_KEYWORDS,
                 stage: list = STAGE_KEYWORD,
                 tier: list = TOURNAMENT_TIER):
        self.tournament = tournament
        self.stage = stage
        self.tier = tier
    
    def get_bracket(self,
                     soup,
                     selector = None,
                     depth=0,
                     max_depth=15) -> list:
        try:
            if soup is None or depth > max_depth:
                return None, selector
            
            parent = soup.find_parent("div")

            if parent is None:
                return None, selector
            
            parent_classes = parent.get("class") or []

            sibling = parent.find_previous_sibling("div")

            if not parent_classes:
                return self.get_bracket(soup=parent, selector=selector, depth=depth+1)
            
            if selector is None:
                selector = f".{parent_classes[0]}"
            else:
                selector = f".{parent_classes[0]} > {selector}"
            
            if sibling:
                sibling_classes = sibling.get("class") or []
                if any(c.endswith("header") for c in sibling_classes):
                    depth_to_level ={
                        1: "Grand Final",
                        3: "Final",
                        5: "Semi-Final",
                        7: "Quarter-Final",
                        9: "Round 1",
                    }
                    level = depth_to_level.get(depth)

                    if "upper" in sibling.get_text().lower() and depth > 1:
                        bracket = f"Upper {level}"
                    elif "lower" in sibling.get_text().lower() and depth > 1:
                        bracket = f"Lower {level}"
                    else:
                        bracket = f"{level}"
                    
                    logging.info(f"Get_bracket completed. Found [{selector}] for {bracket} bracket.")
                    return bracket
            
            return self.get_bracket(soup=parent, selector=selector, depth=depth+1)
            
        except Exception as e:
            logging.error(f"Error occurs while executing get_bracket method: {e}")
            print("Error occurs while executing get_bracket method")
    
    def get_detail(self,
                   soup,
                   tier,
                   tournament,
                   stage,
                   bracket) -> list:
        logging.info("Getting detail from get_detail method of Match Scraper class.")
        results = []
        try:
            popup = get_item(soup, ".brkts-popup", exact=True)
            logging.info(f"Found {popup}.")
            logging.info(f"Found {len(popup)} items for popup.")
            timestamp = get_item(popup, selector=".timer-object-datetime-only", exact=True)
            logging.info(f"Found {timestamp}.")
            logging.info(f"Found {len(timestamp)} items for timestamp.")
            date = get_text(timestamp)
            date = parser.parse(date)
            date = date.date()
            logging.info(f"Found match time: {date}")
            
            team_name = get_item(popup, ".name.hidden-xs")
            alias_name = get_item(popup, ".name.visible-xs")
            home_name = get_text(team_name[0])
            home_alias = get_text(alias_name[0])
            logging.info(f"Found {home_name} as {home_alias} for home team.")
            away_name = get_text(team_name[1])
            away_alias = get_text(alias_name[1])
            logging.info(f"Found {away_name} as {away_alias} for away team.")
            
            games = get_item(popup, ".brkts-popup-body-game")
            logging.info(f"Found {len(games)} game(s).")

            # ambil teks score atau result
            score_el = get_item(popup, ".match-info-header-scoreholder-upper", exact=True)
            score_text = get_text(score_el).strip() if score_el else ""

            # cek apakah ini auto-win
            is_autowin = any(k in score_text for k in ["Win", "Winner", "FF", "DQ"])
            is_empty_game = (len(games) == 0) or (len(games) == 1 and not get_text(games[0]).strip())

            if is_autowin or is_empty_game:
                logging.info(f"Auto-win/FF detected ({score_text}). Using fallback.")
                return []

            bans_item = get_item(popup, ".brkts-popup-mapveto__ban-round")
            all_bans = []
            for b in bans_item:
                num = get_text(b).replace("\xa0", " ").strip()[-1]
                idx = int(num) - 1
                while len(all_bans) <= idx:
                    all_bans.append([])
                
                ban_heroes = [get_element(a, "title") for a in get_item(b, "a")]
                all_bans[idx] = ban_heroes
            logging.info(f"Found total {len(all_bans)} banned heroes: {all_bans}")
        
            home_bans, away_bans = [], []
            for i, bans in enumerate(all_bans):
                if bans == []:
                    home_bans.append([])
                    away_bans.append([])
                else:
                    mid = len(bans) // 2
                    home, away = bans[:mid], bans[mid:]
                    home_bans.append(home)
                    away_bans.append(away)
            logging.info(f"Home bans: {home_bans}, Away bans: {away_bans}")
                
            for i, game in enumerate(games, start=1):
                time = get_text(game)[:5].strip()
                duration = time if re.match(r'^\d{1,2}:\d{2}$', time) else np.nan
                logging.info(f"Found duration game: {duration}.")
                map_name = get_text(game)[5:].strip() or "Default"
                logging.info(f"Found map name: {map_name}.")

                icon = get_item(game, ".brkts-result-label", exact=True)
                logging.info(f"Found icon: {icon}.")
                classes = icon.get("class", []) if icon else []
                logging.info(f"Found classes: {classes}.")

                pick_heroes = [get_element(a, "title") for a in get_item(game, "a")]
                logging.info(f"Found {len(pick_heroes)} heroes picked. {pick_heroes}.")
                home_picks, away_picks = pick_heroes[:5], pick_heroes[5:]
                
                results.append({
                    "date": date,
                    "game_num": i,
                    "home_team": home_name,
                    "home_alias": home_alias,
                    "away_team": away_name,
                    "away_alias": away_alias,
                    "home_picks": home_picks,
                    "away_picks": away_picks,
                    "home_bans": home_bans[i-1] if i-1 < len(home_bans) else [],
                    "away_bans": away_bans[i-1] if i-1 < len(away_bans) else [],
                    "duration": duration,
                    "map": map_name,
                    "home_status": "win" if any(c.endswith("win") for c in classes) else "loss",
                    "away_status": "win" if any(c.endswith("loss") for c in classes) else "loss",
                    "tier": tier,
                    "tournament": tournament,
                    "stage": stage,
                    "bracket": bracket
                })
            
            logging.info(f"get_detail method completed.")    
            return results
        
        except Exception as e:
                logging.error(f"Error occurs while executing get_detail method: {e}")
                print("Error occurs while executing get_detail method")
    
    def scrape_match_detail(self, url) -> list:
        logging.info("Getting match detail from scrape_match_detail method of Match Scraper class.")
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
                
                logging.info("Getting soup from get_soup method from scraper_utils. Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Get_soup completed. Soup fetched, extracting items...")
                match_format = get_item(soup, "li")
                context = []
                for i in match_format:
                    text = get_text(i)
                    context.append(text)
                is_elimination = any("elimination" in t.lower() for t in context)
                logging.info(f"This tournament stage has {'Elimination' if is_elimination==True else 'Round Robin'} Format.")
                
                if is_elimination==True:
                    matches = get_item(soup, selector="div.brkts-match")
                    logging.info(f"Get_item completed. Found match: {len(matches)}.")
                    if not matches:
                        logging.info(f"Running get_item method from scraper_utils. Scraping round robin matches ...")
                        matches = get_item(soup, selector="div.brkts-match-has-details")
                        logging.info(f"Get_item method completed. Found {len(matches)} matches.")
                        for match in matches:
                            result = self.get_detail(match, tier, tournament, stage, bracket=stage)
                            for item in result:
                                match_detail.append(item)
                    else:
                        for match in matches:
                            logging.info("Getting bracket from get_bracket method of Match Scraper class.")
                            bracket = self.get_bracket(soup=match)
                            logging.info(f"Scraping matches ...")
                            result = self.get_detail(match, tier, tournament, stage, bracket)
                            for item in result:
                                match_detail.append(item)
                    
                else:
                    logging.info(f"Running get_item method from scraper_utils. Scraping round robin matches ...")
                    matches = get_item(soup, selector="div.brkts-match-has-details")
                    logging.info(f"Get_item method completed. Found {len(matches)} matches.")
                    for match in matches:
                        logging.info(f"Scraping matches ...")
                        result = self.get_detail(match, tier, tournament, stage, bracket=stage)
                        for item in result:
                            match_detail.append(item)
                
                processed.add(current_url)
            logging.info("scrape_match_detail method completed.")
            return match_detail
        
        except Exception as e:
            logging.error(f"Error occurs while executing scrape_match_detail method: {e}")
            print("Error occurs while executing scrape_match_detail method")
    
    def run(self, url):
        logging.info("Running run method of Match Scraper class.")
        match_detail = self.scrape_match_detail(url)
        save_csv(
            dataframe = match_detail,
            filename = "match_detail",
            is_list_of_dict=True
        )
        logging.info("run method completed.")