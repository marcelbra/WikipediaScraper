"""
Author: Marcel Braasch
Email: marcelbraasch@gmail.com

Goethe University Frankfurt
Text Technology Lab
August 2019
"""

from lxml import etree
import requests
from io import StringIO
import urllib.parse
import os

def make_request(title):

    # Get content and parse into html tree
    title = urllib.parse.quote(title)
    url = f"https://de.wikipedia.org/wiki/Spezial:Alle_Seiten?from={title}"
    page = requests.get(url)
    content = page.text
    f = StringIO(content)
    tree = etree.parse(f)

    # Query tree and get unordered list with all titles
    ul = tree.xpath("//ul[@class='mw-allpages-chunk']")[0]

    # Extract the titles ([0] because below every list item is a href item)
    all_titles = [li[0].text for li in ul]

    return all_titles

def save_titles(titles, path = "save.txt"):
    with open(path, "a+") as file:
        for title in titles:
            file.write(title + "\n")

def main():

    first_title = "!"
    titles = make_request(first_title)
    save_titles(titles)
    last_title = titles[-1]
    counter = 1
    while True:
        titles = make_request(last_title)
        last_title = titles[-1]
        save_titles(titles)
        os.system('clear')
        print(f"Page {counter} saved.")
        counter += 1

main()