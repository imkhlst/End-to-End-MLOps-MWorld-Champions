from logger import logging
from constants.scraper_constant import *
from utils.scraper_utils import *

class HeroScraper:
    def __init__(self, base_url: str = BASE_URL):
        self.portal = get_url(get_soup(base_url), "portal:heroes")
    
    def scrape_hero(self):
        logging.info("Running scrape_hero method of Hero Scraper class.")
        result = []
        try:
            for current_url in self.portal:
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                contents = get_item(soup, ".content3")
                for content in contents:
                    roles = get_item(content, "div", exact=True)
                    role_name = get_text(roles)
                    heroes = get_item(content, ".zoom-container")
                    for hero in heroes:
                        hero_name = get_text(hero)
                        logging.info(f"Adding {hero_name} as {role_name} to result.")
                        result.append({
                            "hero_name": hero_name,
                            "role_name": role_name
                        })
            logging.info("Scrape_hero method completed.")

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