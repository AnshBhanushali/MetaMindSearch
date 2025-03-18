import os
import tempfile
import requests
import pytest
from io import BytesIO
from bs4 import BeautifulSoup

# Import functions to test. Adjust the module name if needed.
from imageScrapper import create_session, scrape_page, download_image, scrape_images

# --- Helpers for faking responses ---

class FakeResponse:
    def __init__(self, text=None, content=b"", status_code=200):
        self.text = text or ""
        self._content = content
        self.status_code = status_code
        self.headers = {}

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.RequestException(f"Status code: {self.status_code}")

    def iter_content(self, chunk_size=8192):
        # Return the content in one chunk
        yield self._content

    # Add context manager support.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Test for scrape_page function ---

def test_scrape_page(monkeypatch):
    fake_html = "<html><body><h1>Test Page</h1></body></html>"
    
    def fake_get(url, timeout):
        return FakeResponse(text=fake_html)
    
    # Create a session and monkeypatch its get method.
    session = create_session()
    monkeypatch.setattr(session, "get", fake_get)
    
    soup = scrape_page("http://fakeurl.com", session)
    assert isinstance(soup, BeautifulSoup)
    h1 = soup.find("h1")
    assert h1 is not None
    assert h1.text.strip() == "Test Page"

# --- Test for download_image function ---

def test_download_image(monkeypatch, tmp_path):
    # Create a fake image content
    fake_image_content = b"fakeimagedata"
    fake_url = "http://fakeurl.com/image.jpg"
    
    def fake_get(url, stream, timeout):
        return FakeResponse(content=fake_image_content)
    
    session = create_session()
    monkeypatch.setattr(session, "get", fake_get)
    
    dest_file = tmp_path / "downloaded_image.jpg"
    result = download_image(session, fake_url, str(dest_file))
    
    # Check that the file was written and contains our fake image data.
    assert result == str(dest_file)
    with open(result, "rb") as f:
        content = f.read()
    assert content == fake_image_content

# --- Test for scrape_images function ---

def test_scrape_images(monkeypatch, tmp_path):
    # Create a fake HTML page with multiple image tags.
    fake_html = """
    <html>
      <body>
        <img src="http://fakeurl.com/img1.jpg" />
        <img src="/img2.png" />
        <img src="http://fakeurl.com/img3.gif" />
      </body>
    </html>
    """
    
    # Fake get for the session used in scrape_page.
    def fake_get(url, timeout):
        return FakeResponse(text=fake_html)
    
    # Create a fake download_image that doesn't do actual network calls.
    def fake_download_image(session, img_url, dest_path):
        # Instead of downloading, simply create an empty file.
        with open(dest_path, "wb") as f:
            f.write(b"fake")
        return dest_path

    # Create a session and monkeypatch its get method.
    session = create_session()
    monkeypatch.setattr(session, "get", fake_get)
    
    # Monkeypatch the create_session function in the module.
    # Since your production module is named 'imageScrapper.py', we use that.
    monkeypatch.setattr("imageScrapper.create_session", lambda user_agent=None, max_retries=3, backoff_factor=0.3: session)
    monkeypatch.setattr("imageScrapper.download_image", fake_download_image)
    
    # Use a temporary folder for downloaded images.
    download_folder = str(tmp_path / "images")
    os.makedirs(download_folder, exist_ok=True)
    
    downloaded_files = scrape_images("http://fakeurl.com/gallery", download_folder=download_folder)
    
    # We expect 3 images to be "downloaded"
    assert len(downloaded_files) == 3
    for file_path in downloaded_files:
        assert os.path.exists(file_path)
        with open(file_path, "rb") as f:
            assert f.read() == b"fake"
