from crawler.parser import Parser

def test_parser_extract_links():
    html="""
        <a href="/about">About</a>
        <a href="/contact">Contact</a>"""

    parser=Parser(html,"http://localhost:8000")
    links=parser.get_links()
    assert "http://localhost:8000/about" in links
    assert "http://localhost:8000/contact" in links

def test_normalize_url_removes_fragment():
    parser = Parser("", "https://example.com")

    result = parser.normalize_url(
        "https://example.com/about.html#section"
    )

    assert result == "https://example.com/about.html"


def test_normalize_url_removes_tracking_parameters():
    parser = Parser("", "https://example.com")

    result = parser.normalize_url(
        "https://example.com/about.html?utm_source=google&page=2"
    )

    assert result == "https://example.com/about.html?page=2"


def test_normalize_url_preserves_normal_parameters():
    parser = Parser("", "https://example.com")

    result = parser.normalize_url(
        "https://example.com/products?page=2"
    )

    assert result == "https://example.com/products?page=2"