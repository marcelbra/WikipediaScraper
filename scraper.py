"""
Author: Marcel Braasch
Email: marcelbraasch@gmail.com

Goethe University Frankfurt
Text Technology Lab
September 2019

Scrapes the Wikipedia.
Expects a list of titles names to work with.
Requests the webpage for every title and saves the HTML
content accordingly.
"""

import json
import os
import sys
from itertools import islice
from typing import Dict, List, Optional
from format import Formatter


class Scraper:

    def __init__(self,
                 language: str = "de",
                 script_no: int = None,
                 no_of_scripts: int = None
                ):

        self._config = self._load_config()
        self._script_no = script_no if script_no else int(sys.argv[1])
        self._no_of_scripts = no_of_scripts if no_of_scripts else int(sys.argv[2])
        self._language = language if language else "de"# sys.argv[3]
        self._titles = self._get_titles()
        self._saved_state = self._get_state()
        self._start_index = self._get_start_index()


    @staticmethod
    def _load_config():
        with open("config.json", "r") as file:
            return json.loads(str(file.read()))

    def _get_titles(self):
        """Gets the scraped titles from file and splits the list."""
        with open(self._config["titles_path"], "r") as file:
            titles = eval(file.read())
            titles = self._split(titles)
            return titles

    def _split(self, titles: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Splits the titles list depending on the script number and how
        scripts are run at the same time. Say you're running 10 scripts
        at the same time script number 1 will get the first 10th of the
        titles. Script number two will scrape the second 10th."""
        start_index = 0 if self._script_no == 1 else (int(len(titles) * (self._script_no-1)/self._no_of_scripts) - 1)
        end_index = int(len(titles) * self._script_no/self._no_of_scripts)
        return dict(islice(titles.items(), start_index, end_index))

    def _save_state(self, title):
        """Saves where to continue."""
        path = self._config["state_path"] + f"saved_{self._script_no}.txt"
        try:
            with open(path, "w") as file:
                file.write(title)
        except FileNotFoundError:
            self._create_dir("Saved")
            self._save_state(title)

    def _get_state(self) -> Optional[str]:
        """Reads where to continue."""
        path = self._config["state_path"] + f"saved_{self._script_no}.txt"
        try:
            with open(path, "r") as file:
                return str(file.read())
        except FileNotFoundError:
            return None

    def _get_start_index(self) -> int:
        """Determines index of where to continue by
        the name which is saved in the saved file."""
        count = 0
        if not self._saved_state:
            return count
        for title in self._titles:
            if title == self._saved_state:
                return count
            count += 1

    def _create_dir(self, name: str):
        """Creates a directory at the specified path."""
        os.makedirs(self._config["save_path"] + name)

    def _save_content(self, title: str, content: str):
        """Saves an article at the specified path."""
        title = title.replace("/", "-")
        try:
            # slice to prevent FileTooLongError
            name = self._config["save_path"] + f"Content_{self._script_no}/" + title[:255]
            with open(name + ".txt", "w") as file:
                file.write(content)
        except FileNotFoundError:
            self._create_dir(f"Content_{self._script_no}")
            self._save_content(title, content)

    @staticmethod
    def _notify(index: int, title: str):
        """Printer."""
        os.system('clear')
        print(f"Now scraping: {title}.")
        print(f"File {index}.")


    def scrape(self):
        """Main programm."""
        formatter = Formatter(self._language)
        for index, (main_title, redirects) in enumerate(self._titles.items()):
            # ensures to continue where script left off
            if self._start_index > index:
                continue
            self._notify(index, main_title)
            content = formatter.format_with_title(main_title, redirects, pretty_print=False)
            if not content:  # there are some files that need to be skipped
                continue
            self._save_content(main_title, content)
            self._save_state(main_title)
            print("Sucessfully scrapped.")


s = Scraper()
s.scrape()
