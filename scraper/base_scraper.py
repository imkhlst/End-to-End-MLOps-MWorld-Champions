import requests as re
import pandas as pd
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


BASE_URL = "https://liquipedia.net/mobilelegends/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0; +https://yourdomain.example/)"
}

class base_scrapper:
    def __init__(self, BASE_URL: str, HEADERS: dict):
        self.BASE_URL = BASE_URL
        self.HEADERS = HEADERS
    
    