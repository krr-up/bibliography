#!/usr/bin/env python3
"""
Script to cleanup bibtex records and pretty print them.
"""

import re
import sys
from io import StringIO
from argparse import ArgumentParser
from difflib import ndiff
from collections import OrderedDict
from itertools import chain

import bibtexparser as bp
from bibtexparser.bibdatabase import BibDataStringExpression
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.latexenc import unicode_to_latex_map
from bibtexparser.customization import splitname


def check_min_version():
    """
    Ensure that a new enough version of python and bibtexparser is used.
    """
    if sys.version_info < (3, 10):
        sys.exit("The script requires at least python version 3.10.")
    vers = bp.__version__.split(".")
    if (int(vers[0]), int(vers[1])) < (1, 2):
        sys.exit("The script requires at least bibtexparser version 1.2.")


def is_ascii(x):
    """
    Reurn true if the given string contains ascii symbols only.
    """
    try:
        x.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def apply_on_expression(x, f):
    """
    Apply the function f for converting strings to bibtex expressions as
    returned by the bibtexparser module.
    """
    if isinstance(x, str):
        return f(x)
    if isinstance(x, BibDataStringExpression):
        x.apply_on_strings(f)
    return x


# Map from unicode symbols to latex expressions.
#
# The bibtexparser.latexenc module also maps some ascii characters to unicode
# symbols. Such characters are ignored in the map.
UNICODE_TO_LATEX = {
    key: value for key, value in unicode_to_latex_map.items() if not is_ascii(key)
}
# Character class for latex accents.
LATEX_ACCENTS = "".join(re.escape(k) for k in "=~^.\"'")


def cleanup_expression(x):
    """
    Convert the given string containing unicode symbols into a single line
    string with latex escapes only.
    """
    ret = []
    for char in x:
        if char in (" ", "{", "}"):
            ret.append(char)
        else:
            ret.append(UNICODE_TO_LATEX.get(char, char))

    res = "".join(ret)
    res = re.sub(r"\s+", " ", res)
    res = re.sub(r"\{\\([" + LATEX_ACCENTS + r"])\{([a-zA-Z])\}\}", r"{\\\1\2}", x)
    return res


def cleanup_record(x):
    """
    Cleanup a record as returned by the bibtexparser module.
    """
    for val in x:
        if val in ("ID",):
            continue
        x[val] = apply_on_expression(x[val], cleanup_expression)
        if val.lower() == "pages":
            x[val] = x[val].replace("--", "-")
    return x


def _parser(customization=cleanup_record):
    """
    Return a configured bibtex parser.
    """
    parser = BibTexParser()
    parser.interpolate_strings = False
    parser.customization = customization
    return parser


def _writer(sorted_entries=True):
    """
    Return a configured bibtex writer.
    """
    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = ("ID",) if sorted_entries else None
    writer.display_order = ["title", "author", "editor"]
    return writer


def _fixdb(db):
    """
    Currently sorts the strings in the database.
    """
    db.strings = OrderedDict(sorted(db.strings.items()))
    return db


def format_bib(path):
    """
    Format the given bibliography file.
    """
    # read bibliography
    with open(path, "r") as f:
        db = _fixdb(bp.load(f, _parser()))

    # write the bibliography
    with open(path, "w") as f:
        bp.dump(db, f, _writer())


class NameFormatter:
    """
    Formatter to abbreviate first names.

    It does well with most names. In particular, all names composed of two words
    are handled correctly. For names with more than two words, splitting uses
    bibtex rules, so you may need to fix some of them manually. For example, `Juan
    Carlos Nieves` is correctly parsed as `{Juan Carlos} Nieves` but `Manuel Ojeda
    Aciego` is incorrectly parsed as `{Manuel Ojeda} Aciego`. It manually has to be
    written as `Manuel {Ojeda Aciego}`.

    Names that do not follow bibtex rules but are already present in the
    bibliography are parsed correctly. Such names only have to be adjusted at the
    moment they are introduced.
    """

    def __init__(self, dbs):
        """
        Initialize the name formatter with the special names already present in
        the given databases.
        """
        self.special_names = {}
        self.partial_special_names = set()
        self._init_special_names(chain(*(list(db.entries) for db in dbs)))
        self._init_partial_special_names()

    def _init_special_names(self, entries) -> None:
        """
        Initialize the special names from the entries.
        """
        for entry in entries:
            self._init_special_name(entry.get("author", ""))
            self._init_special_name(entry.get("editor", ""))

    def _match_braces(self, name: str) -> list[tuple[int, int]]:
        """
        Return the list of matching braces in the given string.
        """
        stack = []
        matched_braces = []
        for i, c in enumerate(name):
            if c == "{":
                stack.append(i)
            elif c == "}":
                if stack:
                    matched_braces.append((stack.pop(), i))
        return matched_braces

    def _init_special_name(self, names: str) -> None:
        """
        Initialize the special names in the given names as a list of
        dictionaries representing the bibtex fields.
        """
        for name in names.replace("\n", " ").split(" and "):
            name_dict = splitname(name)

            last_str = name_dict.get("last", [])
            if not last_str:
                continue
            last = name_dict.get("last", [])
            last_str = " ".join(last)
            matched_braces = self._match_braces(last_str)
            if (
                matched_braces
                and matched_braces[-1][0] == 0
                and matched_braces[-1][1] == len(last_str) - 1
            ):
                last = tuple(last_str[1:-1].split())
                self.special_names[last] = name_dict
            von = name_dict.get("von", [])
            if not von:
                continue
            von = " ".join(name_dict.get("von", []))
            matched_braces = self._match_braces(von)
            if (
                matched_braces
                and matched_braces[-1][0] == 0
                and matched_braces[-1][1] == 2
                and von[1].isupper()
            ):
                von = tuple([*(von[1] + von[3:]).split(), *last])
                self.special_names[von] = name_dict

    def _init_partial_special_names(self) -> None:
        """
        Initialize the partial special names.
        self.special_names must be initialized first.
        """
        for words in self.special_names:
            if len(words) > 1:
                for i, _ in enumerate(words[1:]):
                    self.partial_special_names.add(tuple(words[1 + i :]))

    def _format_first_name(self, name: str) -> str:
        """
        Abbreviate the given first name.
        """
        if len(name) > 2 and not name.startswith("{\\"):
            name = f"{name[0]}."
        return name

    def _is_special_name(self, first: tuple, last: tuple) -> bool:
        if last in self.special_names:
            abbrev_first = self._format_first_name(" ".join(first))
            if abbrev_first == " ".join(self.special_names[last]["first"]):
                return True
        return False

    def _split_name(self, name: str) -> dict:
        name_dict = splitname(name)
        first = name_dict.get("first", [])
        von = name_dict.get("von", [])
        last = name_dict.get("last", [])
        if len(first) + len(von) <= 1 or not last:
            return name_dict
        words = first + von + last[:1]
        last = tuple(last[1:])
        prev_s_name = None
        while words:
            lw = words.pop()
            last = tuple([lw, *last])
            if self._is_special_name(words, last):
                prev_s_name = self.special_names[last]
            if last not in self.partial_special_names:
                if prev_s_name:
                    return prev_s_name.copy()
                return name_dict
        return name_dict

    def _join_name(self, name: dict) -> str:
        """
        Concatenate the name represented as a dictionary of its bibtex field into a string.
        Braces are added to the last name if it contains spaces. Braces are added to the the
        first letter of the von part if it is capitalized.
        """
        first = " ".join(name.get("first", []))
        von = " ".join(name.get("von", []))
        if len(von) > 1 and von[0].isupper():
            von = f"{{{von[0]}}}{von[1:]}"
        last = " ".join(name.get("last", []))
        n = len(last) - 1
        if " " in last:
            matched_braces = self._match_braces(last)
            if (
                not matched_braces
                or not matched_braces[-1][0] == 0
                or not matched_braces[-1][1] == n
            ):
                last = f"{{{last}}}"
        jr = " ".join(name.get("jr", []))
        previous = first != ""
        if previous and von:
            von = f" {von}"
        previous = previous or von != ""
        if previous and last:
            last = f" {last}"
        previous = previous or last != ""
        if previous and jr:
            jr = f" {jr}"
        return f"{first}{von}{last}{jr}"

    def _format_name(self, name: str) -> str:
        name_dict = self._split_name(name)
        if "first" in name_dict:
            first_name = " ".join(name_dict["first"])
            name_dict["first"] = [self._format_first_name(first_name)]
        return self._join_name(name_dict)

    def __call__(self, names: str) -> str:
        return " and ".join(
            self._format_name(name) for name in names.replace("\n", " ").split(" and ")
        )


def format_names(*paths):
    """
    Format names in the given bibliography file.
    """
    dbs = []
    for path in paths:
        with open(path, "r") as f:
            dbs.append(bp.load(f, _parser()))
    formatter = NameFormatter(dbs)
    for db in dbs:
        for entry in db.entries:
            if "author" in entry:
                entry["author"] = formatter(entry["author"])
            if "editor" in entry:
                entry["editor"] = formatter(entry["editor"])
    for db, path in zip(dbs, paths):
        with open(path, "w") as f:
            bp.dump(db, f, _writer(sorted_entries=False))


def check_bib(path):
    """
    Check if the given bibliography is correctly formatted.
    """
    # read bibliography
    with open(path, "r") as f:
        in_ = f.read()

    db = _fixdb(bp.loads(in_, _parser()))

    # write the bibliography
    out = StringIO()
    bp.dump(db, out, _writer())

    return [
        x for x in ndiff(in_.splitlines(), out.getvalue().splitlines()) if x[0] != " "
    ]


def run():
    """
    Run the application.
    """
    check_min_version()

    parser = ArgumentParser(
        prog="bibfmt", description="Autoformat and check bibliography."
    )
    subparsers = parser.add_subparsers(
        metavar="command", dest="command", help="available subcommands", required=True
    )
    subparsers.add_parser(
        "check", help="check whether bibliography is correctly formatted"
    )
    subparsers.add_parser("format", help="format the bibliography")
    subparsers.add_parser("format-names", help="format names in the bibliography")

    res = parser.parse_args()

    if res.command == "format":
        format_bib("krr.bib")
        format_bib("procs.bib")
        return 0

    if res.command == "format-names":
        format_names("krr.bib", "procs.bib")
        return 0

    assert res.command == "check"
    diff = check_bib("krr.bib") + check_bib("procs.bib")
    if diff:
        for x in diff:
            print(x, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
