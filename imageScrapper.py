import os
import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_session(user_agent=None, max_retries=3, backoff_factor=0.3):
    """Create a requests session with a retry strategy."""
    session = requests.Session()
    if user_agent:
        session.headers.update({"User-Agent": user_agent})
    retry_strategy = Retry(
        total=max_retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def scrape_page(url, session):
    """Fetch the HTML content of the URL and return a BeautifulSoup object."""
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Error fetching page {url}: {e}")
        raise

def download_image(session, img_url, dest_path):
    """Download an image from the given URL and save it to the destination path."""
    try:
        with session.get(img_url, stream=True, timeout=10) as response:
            response.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        logger.info(f"Downloaded {img_url} to {dest_path}")
        return dest_path
    except requests.RequestException as e:
        logger.error(f"Error downloading {img_url}: {e}")
        return None

def scrape_images(url, download_folder='downloaded_images'):
    """
    Scrapes image URLs from a web page and downloads them.
    
    Parameters:
      url (str): The URL of the web page to scrape.
      download_folder (str): Local folder to save downloaded images.
      
    Returns:
      list: List of paths for successfully downloaded images.
    """
    session = create_session(user_agent="Mozilla/5.0 (compatible; ImageScraper/1.0)")
    soup = scrape_page(url, session)

    # Create download folder if not exists
    os.makedirs(download_folder, exist_ok=True)
    
    # Collect image URLs
    img_tags = soup.find_all('img')
    image_urls = []
    for img in img_tags:
        src = img.get("src")
        if src:
            full_url = src if src.startswith("http") else urljoin(url, src)
            image_urls.append(full_url)

    downloaded_files = []
    for i, img_url in enumerate(image_urls):
        # Determine file extension if possible, default to .jpg
        ext = os.path.splitext(img_url)[1].split('?')[0]
        if ext.lower() not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            ext = ".jpg"
        filename = os.path.join(download_folder, f"img_{i}{ext}")
        result = download_image(session, img_url, filename)
        if result:
            downloaded_files.append(result)
    return downloaded_files

if __name__ == '__main__':
    # Ask the user for the URL containing images.
    image_page_url = input("Enter the URL of the page to scrape images from: ").strip()
    
    if not image_page_url:
        logger.error("No URL provided. Exiting.")
    else:
        try:
            downloaded_images = scrape_images(image_page_url)
            logger.info(f"Downloaded {len(downloaded_images)} images.")
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
