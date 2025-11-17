from dateutil import parser
from logger import logging
from constants.scraper_constant import *
from utils.scraper_utils import *


class PatchScraper:
    def __init__(self, base_url: str = BASE_URL):
        self.portal = get_url(get_soup(base_url), "portal:patches")
    
    def scrape_patch(self):
        logging.info("Running scrape_patch method of Patch Scraper class.")
        result = []
        try:
            for current_url in self.portal:
                logging.info("Fetching soup ...")
                soup = get_soup(current_url)
                logging.info("Soup Fetched, extracting items ...")
                tables = get_item(soup, ".wikitable.collapsible")
                logging.info(f"Found {len(tables)} tables. Select the first two tables.")
                for table in tables[:2]:
                    rows = get_item(table, "td a[href]")
                    logging.info(f"Found {len(rows)} items.")
                    for item in rows:
                        patch = get_element(item, "title")
                        if not patch or not "Patch" in patch:
                            continue
                        logging.info(f"Found {patch}.")
                        
                        date = item.find_parent("td").find_next_sibling("td")
                        date = get_text(date)
                        date = parser.parse(date)
                        date = date.date()
                        logging.info(f"Found release date: {date}.")
                        result.append({
                            "patch": patch,
                            "release_date": date
                        })
            
            logging.info("scrape_patch method completed.")
            return result
        
        except Exception as e:
            logging.error(f"Error occur while executing scrape patch method: {e}.")
            print("Error occur while executing scrape patch method")
    
    def run(self):
        logging.info("Running run method of Patch Scraper class.")
        scrape_patch = self.scrape_patch()
        save_csv(
            dataframe = scrape_patch,
            filename = "patch_detail",
            is_list_of_dict=True
        )
        logging.info("run method completed.")