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

    def fetch(self, url):
        """
        Fetch url content from the given URL
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    def parse(self, html):
        """
        Parse HTML files
        """
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, soup):
        """
        Extract and clean text from bs4 object
        """
        paragraphs = soup.find_all('p')
        text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
        return text
    
    def scrape(self, url):
        """
        Complete pipeline for above functions
        """
        html = self.fetch(url)
        soup = self.parse(html)
        return self.extract_text(soup)