import requests
import time

class Downloader:
    def __init__(self):
        self.session=requests.session()
        self.timeout=10
        self.max_retries=3
        self.session.headers.update({"user-agent":"HTTP-Crawler/1.0"})

    def download(self,url):
        for attempt in range(self.max_retries):
            try:
                response=self.session.get(url,timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.HTTPError as e:
                print(f"HTTP error:{e}")
                return None
            except requests.Timeout:
                print(f"Timeout error:{url} (attempt {attempt+1})")

            except requests.RequestException as e:
                print(f"Download failed:{e} (attempt {attempt+1})")

            if attempt<self.max_retries-1:
                time.sleep(1)

        print(f"Failed after {self.max_retries} attempts:{url}")
        return None
        
        