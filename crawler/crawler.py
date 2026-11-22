from crawler.downloader import Downloader
from crawler.parser import Parser
import redis
from crawler.database import pages
import logging
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

load_dotenv()

logging.basicConfig(level=logging.INFO,format="%(asctime)s-%(levelname)s-%(message)s")
logger=logging.getLogger(__name__)

class Crawler:
    def __init__(self,start_url):
        self.start_url=start_url
        self.redis=redis.Redis(host=os.getenv("REDIS_HOST"),port=int(os.getenv("REDIS_PORT")),decode_responses=True)
        self.downloader=Downloader()
        self.success_count=0
        self.failed_count=0
        self.max_pages=int(os.getenv("MAX_PAGES",100))
        self.max_workers=int(os.getenv("MAX_WORKERS",5))
        self.lock=Lock()

    def process_url(self,url):
        if self.redis.sismember("crawler:visited",url):
            return 
        if self.redis.sismember("crawler:failed",url):
            return
        claimed=self.redis.sadd("crawler:processing",url)

        if not claimed:
            return
        
        try:

            logger.info(f"visiting:{url}")
            response=self.downloader.download(url)
            if response is None:
                self.redis.sadd("crawler:failed",url)
                with self.lock:
                    self.failed_count+=1
                return
            self.redis.sadd("crawler:visited",url)
            pages.update_one({"url":url},{"$set":{"content":response.text}},upsert=True)
            with self.lock:
                self.success_count+=1
            logger.info("saved to MongoDB:%s",url)
            parser=Parser(response.text,url)
            new_links=parser.get_links()

            for link in new_links:
                self.redis.sadd("crawler:pending",link)
        finally:
            self.redis.srem("crawler:processing",url)

    def crawl(self,resume=False):
        if not resume:
            self.redis.delete("crawler:pending","crawler:processing","crawler:visited","crawler:failed")
            self.redis.sadd("crawler:pending",self.start_url)
        elif self.redis.scard("crawler:pending")==0:
            logger.info("No pending URLs available to resume.")
            return self.redis.smembers("crawler:visited")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            while (self.redis.scard("crawler:pending")>0 and self.success_count<self.max_pages):
                remaining_pages=self.max_pages-self.success_count
                urls=[]

                for _ in range(min(self.max_workers,remaining_pages)):
                    if self.success_count>=self.max_pages:
                        break
                    url=self.redis.spop("crawler:pending")

                    if url is None:
                        break
                    urls.append(url)

                if not urls:
                    break
            
                list(executor.map(self.process_url,urls))
            logger.info("\n---Crawl Summary---")
            logger.info("Successfully Crawled:%s",self.success_count)
            logger.info("Failed:%s",self.failed_count)
            return self.redis.smembers("crawler:visited")

if __name__=="__main__":
    crawler=Crawler(os.getenv("START_URL"))
    visited=crawler.crawl()
    print(visited)



        