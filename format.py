"""
Author: Marcel Braasch
Email: marcelbraasch@gmail.com

Goethe University Frankfurt
Text Technology Lab
September 2019

Format raw Wikipedia HTML into Heading and Paragraph
objects which can be further processed by Jsonizer.
"""

from lxml import etree, html
from bs4 import BeautifulSoup, Comment
import re
import requests
from typing import Dict, List, Optional
from wiki_objects import Heading, Paragraph, Skips
from io import StringIO
import json
from time import sleep


class Formatter:

    def __init__(self, language="de"):

        self.language = language
        self.tree = None
        self.title = None

    @staticmethod
    def format_heading(text: str) -> str:
        """Gets text representing a heading and removes
         unwanted parts of it."""
        text = text.replace("[Bearbeiten | Quelltext bearbeiten]", "")[2:-3]
        text = text.replace("[edit]", "")
        return text

    @staticmethod
    def clean_html_encodings(text: str) -> str:
        """Gets text in html format and returns it having
        decoded all html encodings."""
        return str(BeautifulSoup(text, 'html.parser'))

    @staticmethod
    def filter_tags(tag: str) -> bool:
        """Filters if a tag should be further looked at."""
        # have not seen ordered lists yet, maybe add
        valid = ["p", "h2", "h3", "h4", "h5", "h6", "ul"]
        return tag in valid

    def get_links(self, text_html: str, text: str) -> List[Dict[str, str]]:
        """Gets the links from the passed text."""
        soup = BeautifulSoup(text_html, 'html.parser')
        hrefs = [(href.text, href['href'], href['title'])
                 for href in soup.find_all('a') if href.get('title')]

        hyperlinks = []
        for (href_text, link, title) in hrefs:
            # skips phonetic link
            if title == "Liste der IPA-Zeichen":
                continue
            start = 0
            try:
                start = text.index(href_text)
            except ValueError as e:
                self.log(e, "p")
                continue
            end = start + len(href_text)
            hyperlinks.append({'link': link,
                               'display_name': href_text,
                               'article_name': title,
                               'start': start,
                               'end': end})

        return hyperlinks

    def log(self, e: Exception, type: str):
        msg = ""
        if type == "w":
            msg = f"\nSkipping whole file {self.title}\n"
        if type == "p":
            msg= f"\nSkipping 1 paragraph in {self.title}.\n"
        if type == "a":
            msg= f"\nSkipping article_id in {self.title}.\n"
        with open("log.txt", "a") as file:
            file.write(msg)

    def skip(self, heading: str) -> bool:
        """Checks if the current heading or paragraph should
        be skipped."""
        skip_flag = False
        for skip in Skips().get(self.language):
            if skip in heading:
                skip_flag = True
        return skip_flag

    def format_categories(self, cat: str) -> Dict[str, str]:
        """Turn raw category html into a dict."""
        regex = "<li><a href=\"(.*?)\" title=\"(.*?)\">(.*?)</a></li>"
        cats = [{"link": x[0],
                 "category_name": self.clean_html_encodings(x[1]),
                 "display_name": self.clean_html_encodings(x[2])}
                for x in re.compile(regex).findall(cat)][0]
        return cats

    @staticmethod
    def clean_phonetic(text: str) -> str:
        regex = r"(?:/|\[)\.mw.*?\.IPA.*?}(.*?)(?:/|])"
        # Currently replacing completely
        # Can be changed to phonetic string
        # group(1) is the capturing group of the actual
        # group. re.search(regex, t).group(1) returns
        # dɒnəld d͡ʒɒn trʌmp for Donald John Trump.
        text = re.sub(regex, "", text)
        return text

    @staticmethod
    def clean_noprints(soup: BeautifulSoup) -> BeautifulSoup:
        regex = r"<span class=\"metadata noprint\">.*?</span>"
        text = re.sub(regex, "", str(soup))
        soup = BeautifulSoup(text, "html.parser")
        return soup

    @staticmethod
    def paragraphs_to_dict(paragraphs: List[Paragraph]):
        """Expects a list of Paragraph objects (see
        PageFormatter) and serializes it into a dict."""
        ps = []
        for para in paragraphs:
            paragraph = dict()

            # add text
            paragraph["text"] = para.text

            # add headings
            for i in range(1, 7):
                if eval(f"para.h{i}"):
                    paragraph[f"h{i}"] = eval(f"para.h{i}.text")

            # add if skippable
            paragraph["is_skippable"] = para.is_skippable
            ps.append(paragraph)
        return ps

    def format_text(self, text: str) -> str:
        """Remove indices like [23] from text.
        Remove line breaks.
        Remove leading b' and trailing '."""
        text = re.sub(r"(?:\[\d+])+", "", text)
        text = re.sub(r"\\n", "", text)
        text = text[2:-1]
        text = self.clean_phonetic(text)
        return text

    # def format_path(self, path: str, pretty_print: bool) -> str:
    #     """Formats a Wikipedia article. Expects the
    #     path of the local copy in html format and
    #     returns a string in Json format containing
    #     all relevant data."""
    #     with open(path, "r") as file:
    #         return self.get_obj(file, pretty_print)

    def format_with_title(self, title: str, redirects: List[str], pretty_print: bool) -> str:
        """Formats a Wikipedia article. Expects the
        exact name of the article and returns a string
        in Json format containing all relevant data."""
        self.title = title
        url = f"https://{self.language}.wikipedia.org/wiki/" + title
        r = requests.get(url).text
        err_msg = "Our servers are currently under maintenance or experiencing"
        if err_msg in r:
            sleep(10)
            self.format_with_title(title, redirects, pretty_print)
        return self.get_obj(StringIO(r), redirects, pretty_print)

    def get_norm_data(self) -> Optional[List[Dict[str, str]]]:

        if self.language == "de":
            return self._get_norm_data_de()
        elif self.language == "en":
            return self._get_norm_data_en()

    def _get_norm_data_de(self) -> Optional[List[Dict[str, str]]]:
        norm_data_xpath = "//*[@id='normdaten']"
        try:
            norm_data = str(html.tostring(self.tree.xpath(norm_data_xpath)[0]))
        except IndexError:
            return
        soup = BeautifulSoup(norm_data, 'html.parser')
        soup = self.clean_noprints(soup)
        a_tags = soup.find_all('a')
        types = a_tags[:-1:2]  # Is type like GND, NDL, VIAF
        infos = a_tags[1::2]  # Is the actual number/id and its link
        norm_data = []
        # not tested excesivelly if this can fail. Evaluating
        # above types and infos expressions there there should
        # be the same number of types and infos (pairs)
        if len(types) != len(infos):
            return
        try:
            regex = r"Normdaten.\((.*?)\):"
            search_obj = re.search(regex, soup.get_text()).group(1)
            norm_data.append({"norm_data_type": search_obj})
        except AttributeError as e:
            # Article probably has no norm data
            pass
        for i in range(len(types)):
            norm_data.append({'type': types[i].text,
                              'value': infos[i].text,
                              'link': infos[i]["href"]})

        return norm_data

    def _get_norm_data_en(self) -> Optional[List[Dict[str, str]]]:
        # TODO
        return self._get_norm_data_de()

    def get_heading(self):

        heading_xpath = "//h1[@class='firstHeading']"
        heading = str(html.tostring(self.tree.xpath(heading_xpath)[0]))
        soup = BeautifulSoup(heading, 'html.parser')
        heading = soup.select('h1.firstHeading')[0].text.strip()
        return heading

    def get_categories(self):
        categories_xpath = "//*[@id='mw-normal-catlinks']/ul"
        # get all list items in ul
        try:
            categories = [li for li in self.tree.xpath(categories_xpath)[0]]
        except IndexError as e:
            return None  # this happens if scraper is tryingn to scrape "User:xxx"
        # transform all li in str format
        categories = [str(html.tostring(cat)) for cat in categories]
        # transform all li in dict
        categories = [self.format_categories(cat) for cat in categories]
        return categories

    def get_paragraphs_headings(self):

        content_xpath = "//div[@class='mw-parser-output']"
        content = ""
        try:
            content = self.tree.xpath(content_xpath)[0]
        except IndexError as e:
            self.log(e, "w")
            # this is indicating to skip this file
            # There are some titles in dump which just don't exist
            return (None, None)
        elements = [element for element in content
                    if self.filter_tags(element.tag)]

        paragraphs = []

        # Keeps track of which heading is up right now
        h = {
            1: Heading(self.get_heading()),
            2: None,
            3: None,
            4: None,
            5: None,
            6: None
        }

        # iterate over sections xpath query returned
        for element in elements:

            text_html = str(html.tostring(element))
            text = BeautifulSoup(text_html, 'html.parser').get_text()

            # This is a paragraph
            if element.tag == "p" or element.tag == "ul":

                text = self.format_text(text)
                links = self.get_links(text_html, text)
                is_list = element.tag == "u"
                is_skippable = False

                # Check if paragraph is a skippable paragraph
                for i in range(2, 7):
                    if h[i] is not None:
                        if self.skip(h[i].text):
                            is_skippable = True

                # Add paragraph if it has text (sometimes it doesnt)
                if text:
                    paragraph = Paragraph(text, h[1], h[2], h[3], h[4],
                                          h[5], h[6], links, is_list, is_skippable)
                    paragraphs.append(paragraph)
                continue

            # If it gets here its a hading
            # Update heading accordingly and reset higher headings
            for i in range(2, 7):
                if element.tag == f"h{i}":
                    heading = self.format_heading(text)
                    h[i] = Heading(heading)
                    # reset all higher headings
                    for j in range(i, 7):
                        h[j+1] = None


                    try:
                        h[i-1].add_subheading(h[i])  # these are weird user files
                    except AttributeError as e:
                        return None, None
                    continue

        return paragraphs, h[1]

    def get_revision_id(self):
        tree = html.tostring(self.tree)
        soup = BeautifulSoup(tree, 'html.parser')
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        revision_id = ""
        for comment in comments:
            regex = r"and revision id (\d+).*?"
            match_obj = re.search(regex, comment)
            if match_obj:
                revision_id = match_obj.group(1)
            comment.extract()
        return revision_id

    def get_article_id(self):
        article_id_xpath = "//*[@id='t-wikibase']"
        try:
            li = str(html.tostring(self.tree.xpath(article_id_xpath)[0]))
        except IndexError as e:
            self.log(e, "a")
            return None
        regex = r"Special:EntityPage/(.*?)\""
        match_obj = re.search(regex, li)
        article_id = ""
        if match_obj:
            article_id = match_obj.group(1)
        return article_id

    def get_obj(self, filestream: StringIO, redirects: List[str], pretty_print: bool):



        # Create etree object to query html
        self.tree = etree.parse(filestream, etree.HTMLParser())

        # h1 recursively contains all headings
        content = dict()
        paragraphs, h1 = self.get_paragraphs_headings()
        if not paragraphs and not h1:
            return None  # there are some files that need to skipped
        content["headings"] = Heading.to_dict(h1)
        content["paragraphs"] = self.paragraphs_to_dict(paragraphs)
        categories = self.get_categories()
        if not categories:
            return None
        content["categories"] = categories
        content["revision_id"] = self.get_revision_id()
        content["article_id"] = self.get_article_id()
        content["norm_data"] = self.get_norm_data()
        content["redirects"] = [h1.text.replace(" ", "_")] + redirects
        content["raw_html"] = str(html.tostring(self.tree))

        if pretty_print:
            jsonarray = json.dumps(content,
                                   ensure_ascii=False,
                                   indent=4,
                                   separators=(',', ': '))
        else:
            jsonarray = json.dumps(content,
                                   ensure_ascii=False,
                                   separators=(',', ': '))
        return jsonarray

#
f = Formatter()
f.format_with_title("Angeela Merkel", [], False)