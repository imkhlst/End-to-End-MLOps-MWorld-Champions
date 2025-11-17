import warnings
from dateutil import parser
from dateutil.parser import UnknownTimezoneWarning
from urllib.parse import urlparse
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
    
    def get_selector(self,
                     soup,
                     selector,
                     stage,
                     result: list = None,
                     depth=0) -> list:
        logging.info("Running get_selector method of Match Scraper class.")
        try: 
            if result is None:
                result = []
            # Ambil semua elemen child sesuai selector
            elements = soup.select_one(selector)
            if stage == "Wildcard":
                elements = soup.select(selector + " > div")
            logging.info(f"Found {len(elements)} items in elements.")
            for h in elements:
                classes = h.get("class") or []
                logging.info(f"Found class: {classes}.")
                # Skip jika mengandung header / connector
                if not re.search(r"(round-body|round-center|round-lower)", " ".join(classes)):
                    continue
                
                # Bangun selector baru untuk dive in 
                next_selector = f"div.{classes[0]}"
                logging.info(f"Next selector: {next_selector}.")
                
                if stage != "Wildcard":
                    siblings = h.find_parent("div").find_all("div", recursive=False)
                    if len(siblings) > 1:
                        idx = siblings.index(h) + 1
                        next_selector = f"div:nth-child({idx})"
                        logging.info(f"Next selector: {next_selector}.")
                
                depth_to_level ={
                    0: "Grand Final",
                    2: "Final",
                    4: "Semi-Final",
                    6: "Quater-Final",
                    8: "Round 1",
                }
                level = depth_to_level.get(depth, f"Round {depth//2}")
                logging.info(f"Bracket Position: {level}.")
                
                bracket = ""
                if level == "Grand Final" or level == "Decider Match":
                    bracket = level
                else:   
                    bracket = "Upper"
                    if any(s in selector for s in ['div.brkts-round-body > div:nth-child(1) > div:nth-child(3)', 'div.brkts-round-body > div > div:nth-child(3)']):
                        bracket = "lower"
                logging.info(f"Bracket level: {bracket}.")
                
                new_selector = f"{selector} > {next_selector}"
                if any(re.search(r"(center)", c) for c in classes):
                    logging.info(f"Found brkts-round-center in {new_selector}")
                    result.append([new_selector, bracket, level])
                    continue
                else:
                    # Dive deeper secara rekursif
                    logging.info("brkts-round-center not found. Dive in started ...")
                    self.get_selector(soup=soup, selector=new_selector, stage=stage, result=result, depth=depth + 1)
            
            logging.info(f"get_selector method completed. Found {len(result)} items for selector.")
            return result

        except Exception as e:
            logging.error(f"Error occurs while executing get_selector method: {e}")
            print("Error occurs while executing get_selector method")
    
    def get_detail(self,
                   soup,
                   tier,
                   tournament,
                   stage,
                   bracket = None,
                   level = None) -> list:
        logging.info("Running get_detail method of Match Scraper class.")
        if bracket is None:
            bracket = "Group Stage"
        if level is None:
            level = "Group Stage"
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
            
            teams = get_item(popup, ".name.hidden-xs")
            logging.info(f"Found {len(teams)} items for teams.")
            home_team = get_text(teams[0])
            logging.info(f"Found {home_team} items for home team.")
            away_team = get_text(teams[1])
            logging.info(f"Found {away_team} items for away team.")
            
            games = get_item(popup, ".brkts-popup-body-game")
            logging.info(f"Found {len(games)} game(s).")

            # ambil teks score atau result
            score_el = get_item(popup, ".match-info-header-scoreholder-upper", exact=True)
            score_text = get_text(score_el).strip() if score_el else ""

            # cek apakah ini auto-win
            is_autowin = any(k in score_text for k in ["W", "Win", "Winner", "FF", "DQ"])
            is_empty_game = (len(games) == 0) or (len(games) == 1 and not get_text(games[0]).strip())

            if is_autowin or is_empty_game:
                logging.info(f"Auto-win/FF detected ({score_text}). Using fallback.")
                return []

            bans_item = get_item(popup, ".brkts-popup-mapveto__ban-round")
            all_bans = []
            for b in bans_item:
                ban_heroes = [get_element(a, "title") for a in get_item(b, "a")]
                all_bans.extend(ban_heroes)

            logging.info(f"Found total {len(all_bans)} banned heroes: {all_bans}")

            # Pisahkan ban untuk home dan away
            if len(all_bans) >= 10:
                home_bans, away_bans = all_bans[:5], all_bans[5:10]
            else:
                mid = len(all_bans) // 2
                home_bans, away_bans = all_bans[:mid], all_bans[mid:]
            logging.info(f"Home bans: {home_bans}, Away bans: {away_bans}")
                
            for i, game in enumerate(games, start=1):
                duration = get_text(game)[:5].strip() or "00:00"
                logging.info(f"Found duration game: {duration}.")
                map_name = get_text(game)[5:].strip() or "Default"
                logging.info(f"Found map name: {map_name}.")

                icon = get_item(game, "i", exact=True)
                classes = icon.get("class", []) if icon else []
                status = "win" if "fa-check" in classes else "loss"

                pick_heroes = [get_element(a, "title") for a in get_item(game, "a")]
                logging.info(f"Found {len(pick_heroes)} heroes picked. {pick_heroes}.")
                home_picks, away_picks = pick_heroes[:5], pick_heroes[5:]
        
                bans_item = get_item(popup, ".brkts-popup-mapveto__ban-round")
                logging.info(f"Found {len(bans_item)} for bans.")
                results.append({
                    "date": date,
                    "game_num": i,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_picks": home_picks,
                    "away_picks": away_picks,
                    "home_bans": home_bans,
                    "away_bans": away_bans,
                    "duration": duration,
                    "map": map_name,
                    "winner": home_team if status == "win" else away_team,
                    "tier": tier,
                    "tournament": tournament,
                    "stage": stage,
                    "bracket": bracket,
                    "position": level
                })
            
            logging.info(f"get_detail method completed.")    
            return results
        
        except Exception as e:
                logging.error(f"Error occurs while executing get_detail method: {e}")
                print("Error occurs while executing get_detail method")
    
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
                logging.info("Soup fetched, extracting items...")
                is_knoutout = bool(get_item(soup, ".brkts-bracket", exact=True))
                is_group_stage = bool(get_item(soup, ".brkts-matchlist", exact=True))
                logging.info(f"This tournament stage has {'Knockout and Group Stage' if is_knoutout==is_group_stage==True else 'Knoutout' if is_knoutout==True else 'Group Stage'} System.")
                
                if is_group_stage:
                    logging.info(f"Scraping group stage matches ...")
                    matches = get_item(soup, selector="div.brkts-matchlist-match.brkts-match-has-details.brkts-match-popup-wrapper")
                    logging.info(f"Found {len(matches)} items for group stage match.")
                    for match in matches:
                        result = self.get_detail(match, tier=tier, tournament=tournament, stage=stage)
                        for item in result:
                            match_detail.append(item)
                
                if is_knoutout:
                    logging.info(f"Scraping knockout stage matches ...")
                    selectors = self.get_selector(soup=soup, selector='div.brkts-bracket-wrapper > div > div.brkts-round-body', stage=stage)
                    for item in selectors:
                        selector = item[0]
                        bracket = item[1]
                        level = item[2]
                        match = get_item(soup, selector + " > div.brkts-match-has-details", exact=True)
                        logging.info(f"Found match: {match}.")
                        result = self.get_detail(match, tier, tournament, stage, bracket, level)
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
        save_csv(dataframe = match_detail, filename = "match_detail", is_list_of_dict=True)
        logging.info("run method completed.")