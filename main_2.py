from threading import Thread
from scraper import Scraper

def start(i: int):
    s = Scraper("de",i,10)
    s.scrape()


d = dict()


for i in range(10):
    d[i] = Thread(target=start, args=(i,))
    d[i].start()