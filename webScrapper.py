import requests
from bs4 import BeautifulSoup
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScrapper:
    def __init__(self, user_agent='Mozilla/5.0 (compatible; MyScraper/1.0)', timeout=10, max_retries=3, backoff_factor=0.3):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

        # retry strategy
        retry_strategy = Retry(
            total = max_retries,
            read = max_retries,
            connect = max_retries,
            backoff_factor = backoff_factor,
            status_forcelist = [429, 500, 502, 503, 504],
            allowed_methods = frozenset(['GET', 'POST'])
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.timeout = timeout
        