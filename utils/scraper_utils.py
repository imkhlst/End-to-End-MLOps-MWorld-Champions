import requests
import random
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from constants.scraper_constant import BASE_URL, HEADERS


def get_soup(url:str = BASE_URL,
             HEADERS:dict = HEADERS,
             retry:int = 3,
             delay_range = (2, 10)):
    for attempt in range(retry):
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        
        except Exception as e:
            print(f"Attemp {attempt+1} failed: {e}")
            time.sleep(random.uniform(*delay_range))
    
    print(f"Failed to get soup from {url} after {retry} attempts.")
    return None

def absolute(href: str):
    return urljoin(base=BASE_URL, url=href)