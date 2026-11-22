from crawler.crawler import Crawler

def test_crawler_starts_with_url():
    crawler=Crawler("http://localhost:8000")
    assert crawler.start_url=="http://localhost:8000" 

def test_crawler_visits_pages():
    crawler=Crawler("http://localhost:8000")
    visited=crawler.crawl()

    assert "http://localhost:8000" in visited

    assert "http://localhost:8000/about.html" in visited
    assert "http://localhost:8000/contact.html" in visited



