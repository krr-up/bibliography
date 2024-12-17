#!/usr/bin/env python3
"""
Script using the bibtexparser module to format author names in our
bibliography.
- It abbreviates first names: Roland Kaminski becomes R. Kaminski.

It does well with most names. In particular, all the names composed of two
words. For names with more than two words the splitting of first/last names is
in general ambiguous, so you may need to fix some of them manually:
`Juan Carlos Nieves` should be parsed as `{Juan Carlos} Nieves`
`Manuel Ojeda Aciego` as `Manuel {Ojeda Aciego}`.
Protected special names can be added to the `config_authfmt.toml` file.
"""
import sys
import os
import tomllib
import bibtexparser as bp
from splitnames import splitname
from bibfmt import check_min_version, cleanup_record, _parser, _writer


def split_names_to_strs(names: str) -> list[str]:
    """
    Split the given string containing people names into a list of strings representing the name of each person.
    """
    return names.replace("\n", " ").split(" and ")


def format_first_name(name: str) -> str:
    if len(name) > 2 and not name.startswith("{\\"):
        name = f"{name[0]}."
    return name


def format_name_dict(name: dict) -> dict:
    """
    Format firstname represented as a dictionary.
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
    Concatenate the name information into a string.
    """
    first = " ".join(name.get("first", []))
    von = " ".join(name.get("von", []))
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


def config_special_names(config) -> dict[str, str]:
    """
    Return the a dictionary mapping special names to their formatted version.
    """
    special_names = config["special_names"]
    for k, name in special_names.items():
        name = [w.strip() for w in name.split("|")]
        if len(name) == 1 and " " in name[0]:
            matched_braces = match_braces(name[0])
            if (
                not matched_braces
                or not matched_braces[-1][0] == 0
                or not matched_braces[-1][1] == len(name[0]) - 1
            ):
                name[0] = f"{{{name[0]}}}"
        special_names[k] = (
            name[0]
            if len(name) == 1
            else name_dict_to_str(
                format_name_dict(splitname(", ".join(name[1:] + [name[0]])))
            )
        )
    return special_names


CONFIG = tomllib.load(
    open(os.path.join(os.path.dirname(__file__), "config_authfmt.toml"), "rb")
)
CONFIG_SPECIAL_NAMES = config_special_names(CONFIG)


def format_name(name: str) -> str:
    """
    Format the given string containing a person name.
    """
    alpha_name = name.replace("{", "").replace("}", "")
    if alpha_name in CONFIG_SPECIAL_NAMES:
        return CONFIG_SPECIAL_NAMES[alpha_name]
    return name_dict_to_str(format_name_dict(splitname(name)))


def format_names(names: str) -> str:
    """
    Format the given string containing people names.
    """
    return " and ".join(format_name(name) for name in split_names_to_strs(names))


def format_entry_names(entry):
    """
    Format the names in the given entry.
    """
    new_entry = entry.copy()
    if "author" in new_entry:
        new_entry["author"] = format_names(new_entry["author"])
    if "editor" in entry:
        new_entry["editor"] = format_names(entry["editor"])
    return new_entry


def format_entry(entry):
    """
    Format the given entry.
    """
    return format_entry_names(cleanup_record(entry))


def format_bib(path):
    """
    Format the given bibliography file.
    """
    # read bibliography
    with open(path, "r") as f:
        db = bp.load(f, _parser(customization=format_entry))

    # write the bibliography
    with open(path, "w") as f:
        bp.dump(db, f, _writer(sorted_entries=False))


if __name__ == "__main__":
    check_min_version()
    format_bib("krr.bib")
    format_bib("procs.bib")
    sys.exit(0)
