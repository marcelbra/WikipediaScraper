"""
Author: Marcel Braasch
Email: marcelbraasch@gmail.com

Goethe University Frankfurt
Text Technology Lab
Oktober 2019

Expects a Wikipedia redirect dump and a
Wikipedia page dump and returns a dict
mapping main pages to all its redirects.
"""

from collections import defaultdict
import json


class RedirectCreater:

    def __init__(self):

        self._config = self._load_config()
        self._no_title_mapping = self.get_no_title_mapping()
        self._main_redirects_mapping = self.get_main_redirects_mapping()

    @staticmethod
    def _load_config():
        with open("config.json", "r") as file:
            return json.loads(str(file.read()))

    @property
    def main_redirects_mapping(self):
        return self._main_redirects_mapping

    def save(self):
        with open(self._config["dumps_path"] + "main_to_redirect.txt", "w") as file:
            file.write(str(self._main_redirects_mapping))

    def get_main_redirects_mapping(self):
        counter = 0
        redirect_mapping = defaultdict(list)
        with open(self._config["dumps_path"] + "dewiki-20191001-redirect.txt", "r") as file:
            line = file.readline()
            while line:
                delimiter = "INSERT INTO `redirect` VALUES "
                if line.startswith(delimiter):

                    # Gets a list of tuples like this:
                    # (8, 0, 'Anschluss_(Soziologie)', '', '')
                    NULL = "NULL"
                    elements = eval(f"[{line[len(delimiter):-2]}]")

                    for element in elements:

                        # Extract number of title, title name and save it
                        main = element[2]
                        try:
                            redirect = self._no_title_mapping[element[0]]
                        except KeyError:
                            continue
                        redirect_mapping[main].append(redirect)

                    print(f"Complete redirect mapping: Line {counter} done.")
                    counter += 1

                line = file.readline()
        return dict(redirect_mapping)

    def get_no_title_mapping(self):
        no_title_mapping = dict()
        counter = 0
        with open(self._config["dumps_path"] + "dewiki-20191001-page.txt", "r") as file:
            line = file.readline()
            while line:
                delimiter = "INSERT INTO `page` VALUES "
                if line.startswith(delimiter):

                    # Gets a list of tuples like this:
                    # (1, 0, 'Alan_Smithee', '', 0, 0, 0.0864337124735431,
                    # '20190824111515', '20190824111815', 183851697,
                    # 7788, 'wikitext', NULL)

                    NULL = "NULL"
                    elements = eval(f"[{line[len(delimiter):-2]}]")

                    for element in elements:

                        # Extract title id and title name
                        # Save it to dict
                        if element[0] in no_title_mapping:
                            raise Exception("Number-title pair must be unique.")
                        no_title_mapping[element[0]] = element[2]

                    print(f"Number title mapping: Line {counter} done.")
                    counter += 1

                line = file.readline()

        return no_title_mapping


r = RedirectCreater()
r.save()