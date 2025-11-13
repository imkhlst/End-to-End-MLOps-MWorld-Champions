import requests
import random
import time
import json
import pandas as pd
import re
import warnings
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from constants.scraper_constant import BASE_URL, HEADERS
from logger import logging

warnings.filterwarnings("ignore", category=UserWarning)

session = requests.Session()
def absolute(href: str) -> str:
    return urljoin(base=BASE_URL, url=href)

def save_json(data, filename: str) -> json:
    logging.info("Running save_json method of utils.")
    def default(o):
        if isinstance(o, set):
            return list(o)
        raise TypeError(f"Type {type(o)} not serializable.")
    
    with open(f"data/link/{filename}.json", "w") as file:
        json.dump(data, file, default=default)
    logging.info(f"Your file has been save in data/link/{filename}.json. save_json method completed.")

def load_json(filename: str):
    logging.info("Running load_json method of utils.")
    with open(filename) as file:
        data = json.load(file)
    logging.info("load_json method completed.")
    return data

def save_csv(dataframe, filename: str):
    logging.info("Running save_csv method of utils.")
    if not isinstance(dataframe, pd.DataFrame):
        dataframe = pd.DataFrame(dataframe)
    file = dataframe.to_csv(f"data/raw/{filename}.csv")
    logging.info(f"Your file has been save in /raw/{filename}.csv. save_csv method completed.")
    
def get_soup(url: str,
             HEADERS: dict = HEADERS,
             retry: int = 3,
             delay_range = (2, 15)):
    logging.info("Running get_soup method of utils.")
    for attempt in range(retry):
        try:
            response = session.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            logging.info("get_soup method completed.")
            return BeautifulSoup(response.content, "html.parser")
        
        except Exception as e:
            print(f"Attemp {attempt+1} failed: {e}")
            time.sleep(random.uniform(*delay_range))
    
    print(f"Failed to get soup from {url} after {retry} attempts.")
    return None

def get_url(soup, keyword: str) -> set:
    try:
        logging.info("Running get_url method of utils.")
        if soup is None:
            return set()
        url = set()
        content = soup.find(id="mw-content-text")
        for a in content.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/mobilelegends/") or href.startswith("/"):
                if keyword.lower() in href.lower():
                    href = absolute(href)
                    url.add(href)
        logging.info("get_url method completed.")
        return url
    
    except Exception as e:
        logging.error(f"Error occur when running get_url method: {e}")
        print("Error occur when running get_url method")

def get_item(soup, selector: str, exact=False):
    try:
        logging.info("Running get_item method of utils.")
        if soup is None:
            logging.error("Failed to soup.")
            return []
        
        if exact==True:
            items = soup.select_one(selector)
        
        else:
            items = soup.select(selector)
            
        logging.info("get_item method completed.")
        return items
    
    except Exception as e:
        logging.error(f"Error occur when running get_item method: {e}")
        print("Error occur when running get_item method")

def get_text(item) -> str:
    try:
        logging.info("Running get_text method of utils.")
        text = item.get_text().encode('utf-8').decode('unicode_escape')
        logging.info("get_text method completed.")
        return text
    
    except Exception as e:
        logging.error(f"Error occur when running get_text method: {e}")
        print("Error occur when running get_text method")

def get_element(item, element: str):
    try:
        logging.info("Running get_attribut method of utils.")
        text = item.get(element)
        logging.info("get_attribut method completed.")
        return text
    
    except Exception as e:
        logging.error(f"Error occur when running get_element method: {e}")
        print("Error occur when running get_element method")
    
def get_selector(soup, selector, result=None):
    try:
        logging.info("Running get_selector method of utils.")
        if result is None:
            result = set()
            
        for h in soup.select(selector):
            classes = h.get("class") or []
            if any(re.search(r"(header|connector)", c) for c in classes):
                continue
            
            new_selector = selector + f" > div.{classes[0]}"
            if any(re.search(r"(center)", c) for c in classes):
                result.add(new_selector)
            
            else:
                get_selector(soup, new_selector, result)
        
        return result
    
    except Exception as e:
        logging.error(f"Error occur when running get_selector method: {e}")
        print("Error occur when running get_selector method")