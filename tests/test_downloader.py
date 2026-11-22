from unittest.mock import Mock,patch
import requests
from crawler.parser import Parser

from crawler.downloader import Downloader

def test_download_success():
    downloader=Downloader()
    fake_response=Mock()

    fake_response.raise_for_status.return_value=None

    with patch.object(downloader.session,"get",return_value=fake_response):
        response=downloader.download("https://example.com")
    assert response==fake_response

def test_download_404():
    downloader=Downloader()
    fake_response=Mock()

    fake_response.raise_for_status.side_effect=requests.HTTPError("404 Not Found")

    with patch.object(downloader.session,"get",return_value=fake_response):
        response=downloader.download("https://example.com")
    assert response is None

def test_download_timeout():
    downloader=Downloader()

    with patch.object(downloader.session,"get",side_effect=requests.Timeout("Request timed out")):
        response=downloader.download("https://example.com")
    assert response is None

def test_download_connection_error():
    downloader=Downloader()

    with patch.object(downloader.session,"get",side_effect=requests.ConnectionError("Connection failed")):
        response=downloader.download("https://example.com")
    assert response is None

def test_get_links():
    html="""
    <a href="/about">About</a>
    <a href="/contact">Contact</a>
    <a href="https://example.com/products">Products</a>
    <a href="https://google.com/products">Google</a>
    <a>missing href</a>"""

    parser=Parser(html,"https://example.com")
    links=parser.get_links()
    assert "https://example.com/about" in links
    assert "https://example.com/contact" in links
    assert "https://example.com/products" in links
    assert "https://google.com" not in links



