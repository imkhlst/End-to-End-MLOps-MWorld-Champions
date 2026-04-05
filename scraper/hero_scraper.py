from logger import logging
from constants.scraper_constant import *
from utils.scraper_utils import *

class HeroScraper:
    def __init__(self):
        self.portal = urljoin(base=BASE_URL, url="/mobilelegends/Portal:Heroes")
    
    def scrape_hero(self):
        logging.info("Running scrape_hero method of Hero Scraper class.")
        result = []
        try:
            logging.info("Fetching soup ...")
            soup = get_soup(self.portal)
            logging.info("Soup Fetched, extracting items ...")
            contents = get_item(soup, ".content3")
            for content in contents:
                roles = get_item(content, ".white-text")
                for role in roles:
                    role_name = get_text(role).split()[0]
                    heroes = get_item(role, ".zoom-container")
                    for hero in heroes:
                        hero_name = get_text(hero)
                        logging.info(f"Adding {hero_name} as {role_name} to result.")
                        result.append({
                            "hero_name": hero_name,
                            "role_name": role_name
                            })
            logging.info("Scrape_hero method completed.")
            return list(result)

        except Exception as e:
            logging.error(f"Error occur while executing scrape_hero method: {e}.")
            print(f"Error occur while executing scrape_hero method.")
    
    def run(self):
        logging.info("Running run method of Hero Scraper class.")
        scrape_hero = self.scrape_hero()
        save_csv(
            dataframe = scrape_hero,
            filename = "hero_detail",
            is_list_of_dict=True
        )
        logging.info("run method completed.")