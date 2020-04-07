from typing import Dict, List

class Skips:

    def get(self, language: str) -> List[str]:

        if language == "de":
            return self._german_skippables()
        elif language == "en":
            return self._english_skippables()

    def _german_skippables(self) -> List[str]:
        skips = ["Einzelnachweis", "Einzelnachweise", "Weblink",
                 "Weblinks", "Literatur", "Persönlichkeit",
                 "Persönlichkeiten", "Zitat",  "Medien",
                 "Film", "Filme", "Filmographie", "Hochschulschriften",
                 "Schriften", "Preis", "Preise", "Quelle", "Quellen",
                 "Siehe auch", "Auszeichnung", "Auszeichnungen",
                 "Diskographie", "Diskografie", "Werk", "Werke",
                 "Weiterführende Informationen", "Ehrung",
                 "Weiterführende Informationenen", "Ehrungen",
                 "Veröffentlichungen", "Veröffentlichung"]
        skips_1 = [skip + "(Auswahl)" for skip in skips]
        skips_2 = [skip + " (Auswahl)" for skip in skips]
        skips = skips + skips_1 + skips_2
        return skips

    def _english_skippables(self) -> List[str]:
        # TODO
        return self._german_skippables()

class Heading:

    def __init__(self, text):
        self._text = text
        self._subheadings = []

    def add_subheading(self, sub):
        self._subheadings.append(sub)

    @property
    def text(self):
        return self._text

    @property
    def subheadings(self):
        return self._subheadings

    @classmethod
    def to_dict(cls, _obj):

        def _to_dict(d, c=1):
            e = dict()
            e[f"h{c}_heading"] = d.text
            if d.subheadings:
                e[f"h{c+1}_headings"] = [_to_dict(sub, c+1) for sub in d.subheadings]
            return e

        return _to_dict(_obj)


class Paragraph:

    def __init__(self, text: str,
                 h1: Heading,
                 h2: Heading = None, h3: Heading = None, h4: Heading = None,
                 h5: Heading = None, h6: Heading = None,
                 links: List[Dict[str, str]] = None,
                 is_list: bool = False,
                 is_skippable: bool = False):
        self._text = text
        self._h1 = h1
        self._h2 = h2
        self._h3 = h3
        self._h4 = h4
        self._h5 = h5
        self._h6 = h6
        self._links = links
        self._is_list = is_list
        self._is_skippable = is_skippable


    @property
    def links(self):
        return self._links

    @property
    def is_list(self):
        return self._is_list

    @property
    def is_skippable(self):
        return self._is_skippable

    @property
    def text(self):
        return self._text

    @property
    def h1(self):
        return self._h1

    @property
    def h2(self):
        return self._h2

    @property
    def h3(self):
        return self._h3

    @property
    def h4(self):
        return self._h4

    @property
    def h5(self):
        return self._h5

    @property
    def h6(self):
        return self._h6