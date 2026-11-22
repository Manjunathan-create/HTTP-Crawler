from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse,urldefrag,parse_qsl,urlencode,urlunparse

class Parser:
    def __init__(self,html,base_url):
        self.html=html
        self.soup=BeautifulSoup(html,"html.parser")
        self.base_url=base_url
        self.domain=urlparse(base_url).netloc


    def normalize_url(self,url):
        url,_=urldefrag(url)
        tracking_params={"utm_source",
                         "utm_medium",
                         "utm_campaign",
                         "utm_term",
                         "utm_content",
                         "fbclid"}
        parsed_url=urlparse(url)
        query_params=parse_qsl(parsed_url.query,keep_blank_values=True)

        filtered_params=[]

        for key,value in query_params:
            if key not in tracking_params:
                filtered_params.append((key,value))
        clean_query=urlencode(filtered_params)
        clean_url=urlunparse((parsed_url.scheme,
                                parsed_url.netloc,
                                parsed_url.path,
                                parsed_url.params,
                                clean_query,
                                ""))
        return clean_url

    def get_links(self):
        links=set()

        for tag in self.soup.find_all("a",href=True):
            href=tag["href"].strip()
            if not href:
                continue
            absolute_url=urljoin(self.base_url,href)
            absolute_url=self.normalize_url(absolute_url)
            parsed_url=urlparse(absolute_url)
            if parsed_url.scheme not in ("http","https"):
                continue
            if parsed_url.netloc!=self.domain:
                continue
            links.add(absolute_url)
        return list(links)

    def get_title(self):
        if self.soup.title:
            return self.soup.title.string.strip()
        return None


if __name__=="__main__":
    parser=Parser("","https://example.com")
    result=parser.normalize_url("https://example.com/products?page=2&utm_source=facebook#reviews")
    print(result)