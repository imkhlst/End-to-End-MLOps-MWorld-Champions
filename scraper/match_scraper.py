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
                     selector=None,
                     depth=0,
                     max_depth=15) -> list:
        try:
            if soup is None or depth > max_depth:
                return None, selector
            
            parent = soup.find_parent("div")

            if parent is None:
                return None, selector
            
            parent_classes = parent.get("class") or []

            if not parent_classes:
                return self.get_bracket(soup=parent, selector=selector, depth=depth+1)
            
            sibling = parent.find_previous_sibling("div")
            
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
                
                sibling = sibling.find_previous_sibling("div")
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
            timestamp = get_item(popup, ".timer-object-datetime-only", exact=True)
            logging.info(f"Found {timestamp}.")
            logging.info(f"Found {len(timestamp)} items for timestamp.")
            date = get_text(timestamp)
            # date = parser.parse(date)
            # date = date.date()
            logging.info(f"Found match time: {date}")
            
            team_list = get_item(popup, ".name.visible-xs a")
            # alias_name = get_item(popup, ".name.visible-xs")
            home_href = get_element(team_list[0], "href")
            if "index" in home_href:
                home_name = get_element(team_list[0], "title")

            else:
                home_url = absolute(home_href)
                home_soup = get_soup(home_url)
                name_box = get_item(home_soup, "h1.firstHeading", exact=True)
                home_name = get_text(name_box)
            
            home_name = re.sub(r"\(.*?\)", "", home_name).strip()
            home_alias = get_text(team_list[0])
            logging.info(f"Found {home_name} as {home_alias} for home team.")

            away_href = get_element(team_list[1], "href")
            if "index" in away_href:
                away_name = get_element(team_list[1], "title")

            else:
                away_url = absolute(away_href)
                away_soup = get_soup(away_url)
                name_box = get_item(away_soup, "h1.firstHeading", exact=True)
                away_name = get_text(name_box)
            
            away_name = re.sub(r"\(.*?\)", "", away_name).strip()
            away_alias = get_text(team_list[1])
            logging.info(f"Found {away_name} as {away_alias} for away team.")
            
            games = get_item(popup, ".brkts-popup-body-game")
            if len(games) == 0:
                games = get_item(popup, ".brkts-popup-body-grid-row")
                if len(games) == 0:
                    score_box = popup.select(".match-info-header-scoreholder-upper")
                    bo_box = popup.select(".match-info-header-scoreholder-lower")

                    # cek apakah ini auto-win atau win by
                    score_text = get_text(score_box).strip() if score_box else ""
                    is_autowin = any(k in score_text for k in ["Win", "Winner", "FF", "DQ"])

                    if is_autowin:
                        logging.info(f"Auto-win/FF detected ({score_text}). Winner takes full score.")
                        total_game = int(get_text(bo_box)[-2]) - 1
                    
                    else:
                        logging.info(f"This match does not have a statistic record.")
                        total_game = int(score_text[0]) + int(score_text[2])

                    for i in range(0, total_game):
                        results.append({
                            "date": date,
                            "game_num": i,
                            "home_team": home_name,
                            "home_alias": home_alias,
                            "away_team": away_name,
                            "away_alias": away_alias,
                            "home_picks": [],
                            "away_picks": [],
                            "home_bans": [],
                            "away_bans": [],
                            "duration": np.nan,
                            "map": np.nan,
                            "home_status": "win" if any(t in ["1", "W", "Win", "Winner"] for t in score_box[0].get_text()) else "loss",
                            "away_status": "loss" if any(t in ["1", "W", "Win", "Winner"] for t in score_box[0].get_text()) else "win",
                            "tier": tier,
                            "tournament": tournament,
                            "stage": stage,
                            "bracket": bracket
                        })
                        logging.info(f"get_detail method completed. get {len(results)} game total for details.")    
                        return results
                    
            logging.info(f"Found {len(games)} game(s).")

            # # ambil teks score atau result
            # score_el = get_item(popup, ".match-info-header-scoreholder-upper", exact=True)
            # score_text = get_text(score_el).strip() if score_el else ""

            # # cek apakah ini auto-win
            # is_autowin = any(k in score_text for k in ["Win", "Winner", "FF", "DQ"])
            # is_empty_game = (len(games) == 0) or (len(games) == 1 and not get_text(games[0]).strip())

            # if is_autowin or is_empty_game:
            #     logging.info(f"Auto-win/FF detected ({score_text}). Using fallback.")
            #     return []

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
                    home_bans.append([np.nan, np.nan, np.nan, np.nan, np.nan])
                    away_bans.append([np.nan, np.nan, np.nan, np.nan, np.nan])
                else:
                    mid = len(bans) // 2
                    home, away = bans[:mid], bans[mid:]
                    home_bans.append(home)
                    away_bans.append(away)
            logging.info(f"Home bans: {home_bans}, Away bans: {away_bans}")
                
            for i, game in enumerate(games, start=1):
                time = get_item(game, ".brkts-popup-body-grid-row-detail", exact=True)
                if not time:
                    time = get_item(game, ".brkts-popup-spaced", exact=True)
                duration = get_text(time)
                map_name = "default"
                map = get_item(game, ".brkts-popup-comment", exact=True)
                if map:
                    map_name = get_text(map)
                    if map_name == "":
                        map_name = np.nan
                if ":" not in duration:
                    duration = np.nan
                    map_name = np.nan
                logging.info(f"Found duration game: {duration}.")
                logging.info(f"Found map name: {map_name}.")

                icon = get_item(game, ".generic-label", exact=True)
                classes = icon.get("data-label-type", []) if icon else []
                if icon is None:
                    icon = get_item(game, ".brkts-result-label", exact=True)
                    classes = icon.get("class", []) if icon else []
                logging.info(f"Found icon: {icon}.")
                logging.info(f"Found classes: {classes}.")

                pick_heroes = [get_element(a, "title") for a in get_item(game, "a")]
                logging.info(f"Found {len(pick_heroes)} heroes picked. {pick_heroes}.")
                home_picks, away_picks = pick_heroes[:5], pick_heroes[5:]
                
                results.append({
                    "date": date,
                    "game_num": int(i),
                    "home_team": home_name,
                    "home_alias": home_alias,
                    "away_team": away_name,
                    "away_alias": away_alias,
                    "home_picks": home_picks,
                    "away_picks": away_picks,
                    "home_bans": home_bans[i-1] if i-1 < len(home_bans) else [np.nan, np.nan, np.nan, np.nan, np.nan],
                    "away_bans": away_bans[i-1] if i-1 < len(away_bans) else [np.nan, np.nan, np.nan, np.nan, np.nan],
                    "duration": duration,
                    "map": map_name,
                    "home_status": "win" if "win" in classes or any("win" in t.lower() for t in classes) else "loss",
                    "away_status": "loss" if "win" in classes or any("win" in t.lower() for t in classes) else "win",
                    "tier": tier,
                    "tournament": tournament,
                    "stage": stage,
                    "bracket": bracket
                })
            
            logging.info(f"get_detail method completed. get {len(results)} game total for details.")    
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
                is_round_robin = any("robin" in t.lower() for t in context)
                is_swiss = any("swiss" in t.lower() for t in context)
                logging.info(f"This tournament stage has {'Elimination/Round Robin' if is_elimination==True and is_round_robin==True else 'Elimination' if is_elimination==True else 'Round Robin' if is_round_robin==True else 'Swiss' if is_swiss==True else 'GSL'} Format.")
                
                if is_round_robin or is_swiss:
                    logging.info(f"Running get_item method from scraper_utils. Scraping round robin / swiss matches ...")
                    matches = get_item(soup, selector=".brkts-matchlist-match")
                    logging.info(f"Get_item method completed. Found {len(matches)} matches.")
                    for match in matches:
                        logging.info(f"Scraping matches ...")
                        result = self.get_detail(match, tier, tournament, stage, bracket="Group Stage")
                        for item in result:
                            match_detail.append(item)

                if is_elimination:
                    matches = get_item(soup, selector="div.brkts-match")
                    if not matches:
                        logging.info(f"Running get_item method from scraper_utils. Scraping round robin matches ...")
                        matches = get_item(soup, selector="div.brkts-matchlist-match")
                        logging.info(f"Get_item method completed. Found {len(matches)} matches.")
                        for match in matches:
                            logging.info(f"Scraping matches ...")
                            result = self.get_detail(match, tier, tournament, stage, bracket=stage)
                            for item in result:
                                match_detail.append(item)
                    else:
                        logging.info(f"Running get_item method from scraper_utils. Scraping elimination matches ...")
                        logging.info(f"Get_item completed. Found match: {len(matches)} matches.")
                        for match in matches:
                            logging.info("Getting bracket from get_bracket method of Match Scraper class.")
                            bracket = self.get_bracket(soup=match)
                            logging.info(f"Scraping matches ...")
                            result = self.get_detail(match, tier, tournament, stage, bracket)
                            for item in result:
                                match_detail.append(item)

                else:
                    logging.info(f"Running get_item method from scraper_utils. Scraping GSL matches ...")
                    matches = get_item(soup, selector="div.brkts-match")
                    logging.info(f"Get_item method completed. Found {len(matches)} matches.")
                    for match in matches:
                        logging.info("Getting bracket from get_bracket method of Match Scraper class.")
                        bracket = self.get_bracket(soup=match)
                        logging.info(f"Scraping matches ...")
                        result = self.get_detail(match, tier, tournament, stage, bracket)
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