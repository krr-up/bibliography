#!/usr/bin/env python3
"""
Script using the bibtexparser module to format author names in our
bibliography.
- It abbreviates first names: Roland Kaminski becomes R. Kaminski.

It does well with most names. In particular, all the names composed of two words. 
For names with more than two words the splitting of first/last names uses the
bibtex rules, so you may need to fix some of them manually: The name 
`Juan Carlos Nieves` is correctly parsed as `{Juan Carlos} Nieves` but the name
`Manuel Ojeda Aciego` is analogously and incorrectly parsed as to `{Manuel Ojeda} Aciego`.
It should be parsed as `Manuel {Ojeda Aciego}`. 

Names that do not follow the bibtex rules but already present in the bibliography are parsed correctly.
For instance, if `{Manuel Ojeda} Aciego` is already present in the bibliography in that format, new
entries with `Manuel Ojeda Aciego` will be parsed correctly. This means that names that do not follow
 the bibtex rules only need to be protected by braces the first time they are introduced in the bibliography.
"""
from itertools import chain
import sys
from typing import Iterator, Optional
import bibtexparser as bp
from bibtexparser.customization import splitname
from bibfmt import check_min_version, cleanup_record, _parser, _writer

from pprint import pprint


def split_names_to_strs(names: str) -> list[str]:
    """
    Split the given string containing people names into a list of strings representing the name of each person.
    """
    return names.replace("\n", " ").split(" and ")


def format_first_name(name: str) -> str:
    """
    Abbreviate the given first name.
    """
    if len(name) > 2 and not name.startswith("{\\"):
        name = f"{name[0]}."
    return name


def format_name_dict(name: dict) -> dict:
    """
    Abbreviate the given first name of a name represented as a dictionary of its bibtex fields.
    """
    if "first" in name:
        first_name = " ".join(name["first"])
        name["first"] = [format_first_name(first_name)]
    return name


def match_braces(name: str) -> list[tuple[int, int]]:
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


def name_dict_to_str(name: dict) -> str:
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
        matched_braces = match_braces(last)
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


class NameFormatter:

    def __init__(self, dbs):
        """
        Initialize the name formatter with the special names already present in the given databases.
        """
        self.special_names = dict()
        self.partial_special_names = set()
        self.__init_special_names(chain(*(list(db.entries) for db in dbs)))
        self.__init_partial_special_names()
        # for k, name in self.special_names.items():
        #     print(" ".join(chain(name["first"], name["von"], name["last"])), "\t\t", k)

    def __init_special_names(self, entries) -> None:
        """
        Initialize the special names from the entries.
        """
        entries = list(entries)
        for entry in entries:
            self.__init_special_names_from_dict(entry.get("author", ""))
            self.__init_special_names_from_dict(entry.get("editor", ""))

    def __init_special_names_from_dict(self, names: list[dict]) -> None:
        """
        Initialize the special names in the given names as a list of dictionaries representing the bibtex fields.
        """
        for name_dict in names:
            last_str = name_dict.get("last", [])
            if not last_str:
                continue
            last = name_dict.get("last", [])
            last_str = " ".join(last)
            matched_braces = match_braces(last_str)
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
            matched_braces = match_braces(von)
            if (
                matched_braces
                and matched_braces[-1][0] == 0
                and matched_braces[-1][1] == 2
                and von[1].isupper()
            ):
                von = tuple([*(von[1] + von[3:]).split(), *last])
                self.special_names[von] = name_dict

    def __init_partial_special_names(self) -> None:
        """
        Initialize the partial special names.
        self.special_names must be initialized first.
        """
        for words in self.special_names:
            if len(words) > 1:
                for i, _ in enumerate(words[1:]):
                    self.partial_special_names.add(tuple(words[1 + i :]))

    def is_special_name(self, first: tuple, last: tuple) -> bool:
        if last in self.special_names:
            abbrev_first = format_first_name(" ".join(first))
            if abbrev_first == " ".join(self.special_names[last]["first"]):
                return True
        return False

    def _special_name_application(self, name: dict) -> dict:
        first = name.get("first", [])
        von = name.get("von", [])
        last = name.get("last", [])
        if len(first) + len(von) <= 1 or not last:
            return name
        words = first + von + last[:1]
        last = tuple(last[1:])
        prev_s_name = None
        while words:
            lw = words.pop()
            last = tuple([lw, *last])
            if self.is_special_name(words, last):
                prev_s_name = self.special_names[last]
            if not last in self.partial_special_names:
                if prev_s_name:
                    return prev_s_name.copy()
                return name
        return name

    def format_name(self, name: dict) -> dict:
        """
        Format the a person's name.
        """
        name = format_name_dict(self._special_name_application(name))
        return name

    def format_names(self, names: list[dict]) -> list[dict]:
        """
        Format the a list of people's names.
        """
        return [self.format_name(name) for name in names]

    def format_entry_names(self, entry):
        """
        Format the names in the given entry.
        """
        new_entry = entry.copy()
        if "author" in new_entry:
            new_entry["author"] = self.format_names(new_entry["author"])
        if "editor" in entry:
            new_entry["editor"] = self.format_names(entry["editor"])
        return new_entry


def entry_names_to_dict(entry: dict) -> dict:
    """
    Format the names in the given entry.
    """
    new_entry = entry.copy()
    if "author" in new_entry:
        new_entry["author"] = [
            splitname(name) for name in split_names_to_strs(new_entry["author"])
        ]
    if "editor" in entry:
        new_entry["editor"] = [
            splitname(name) for name in split_names_to_strs(entry["editor"])
        ]
    return new_entry


def entries_names_to_dict(entries: Iterator[dict]) -> Iterator[dict]:
    for entry in entries:
        yield entry_names_to_dict(entry)


def entry_names_to_str(entry: dict) -> dict:
    """
    Format the names in the given entry.
    """
    new_entry = entry.copy()
    if "author" in new_entry:
        new_entry["author"] = " and ".join(
            name_dict_to_str(name) for name in new_entry["author"]
        )
    if "editor" in entry:
        new_entry["editor"] = " and ".join(
            name_dict_to_str(name) for name in new_entry["editor"]
        )
    return new_entry


def dbs_open(*paths: str) -> list[bp.bibdatabase.BibDatabase]:
    """
    Open the given bibliography files.
    """
    dbs = []
    for path in paths:
        with open(path, "r") as f:
            dbs.append(bp.load(f, _parser(customization=cleanup_record)))
    return dbs


def dbs_names_str_to_dict(*dbs: dict) -> None:
    """
    Convert the names in the given databases from strings to dictionaries.
    """
    for db in dbs:
        db.entries = list(entries_names_to_dict(db.entries))


def entries_names_to_str(entries: Iterator[dict]) -> Iterator[dict]:
    """
    Convert the names in the given entries from dictionaries to strings.
    """
    for entry in entries:
        yield entry_names_to_str(entry)


def dbs_names_dict_to_str(*dbs: dict) -> None:
    """
    Convert the names in the given databases from dictionaries to strings.
    """
    for db in dbs:
        db.entries = list(entries_names_to_str(db.entries))


def dbs_write(*dbs_and_paths: tuple[dict, str]) -> None:
    """
    Write the given databases to the given paths.
    """
    for db, path in dbs_and_paths:
        with open(path, "w") as f:
            bp.dump(db, f, _writer(sorted_entries=False))


def dbs_format_names(
    formatter: NameFormatter,
    *dbs: dict,
) -> None:
    """
    Format the names in the given databases.
    """
    for db in dbs:
        db.entries = [formatter.format_entry_names(entry) for entry in db.entries]


def format_bib(*paths):
    """
    Format the given bibliography file.
    """
    dbs = dbs_open(*paths)
    dbs_names_str_to_dict(*dbs)
    formatter = NameFormatter(dbs)
    dbs_format_names(formatter, *dbs)
    dbs_names_dict_to_str(*dbs)
    dbs_write(*zip(dbs, paths))


if __name__ == "__main__":
    check_min_version()
    format_bib("krr.bib", "procs.bib")
    sys.exit(0)
