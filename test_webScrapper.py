import pytest
from bs4 import BeautifulSoup
from webScrapper import WebScrapper

# FakeResponse to simulate requests.Response
class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP Error: status code {self.status_code}")

# DummySession to override the real requests.Session in tests
class DummySession:
    def __init__(self, response):
        self.response = response
        self.headers = {}

    def get(self, url, timeout):
        return self.response

@pytest.fixture
def scraper():
    return WebScrapper()

def test_extract_text(scraper):
    html = "<html><body><p>Paragraph 1</p><p>Paragraph 2</p></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    extracted_text = scraper.extract_text(soup)
    expected_text = "Paragraph 1\nParagraph 2"
    assert extracted_text == expected_text

def test_fetch_success(scraper):
    fake_html = "<html><body><p>Test Paragraph</p></body></html>"
    fake_response = FakeResponse(fake_html, 200)
    scraper.session = DummySession(fake_response)
    html = scraper.fetch("https://www.bbc.com/news")
    assert html == fake_html

def test_fetch_failure(scraper):
    fake_response = FakeResponse("Not Found", 404)
    scraper.session = DummySession(fake_response)
    with pytest.raises(Exception):
        scraper.fetch("https://www.bbc.com/news")

def test_scrape(scraper):
    fake_html = "<html><body><p>Test Paragraph</p></body></html>"
    fake_response = FakeResponse(fake_html, 200)
    scraper.session = DummySession(fake_response)
    text = scraper.scrape("https://www.bbc.com/news")
    assert text == "Test Paragraph"
