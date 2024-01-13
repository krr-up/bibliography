#!/usr/bin/env python3
'''
Script using the bibtexparser module to format author names in our bibliography.
'''
import sys
import json
import bibtexparser as bp
from splitnames import splitname
from bibfmt import check_min_version, cleanup_record, _parser, _writer

def split_names_to_strs(names: str) -> list[str]:
    '''
    Split the given string containing people names into a list of strings representing the name of each person.
    '''
    return names.replace("\n", " ").split(' and ')

def format_first_name(name: str) -> str:
    if len(name) > 2 and not name.startswith("{\\"):
        name = f"{name[0]}."
    return name

def format_name_dict(name: dict) -> dict:
    '''
    Format name reprented as a dictionary.
    '''
    if "first" in name:
        first_name = " ".join(name["first"])
        name["first"] = [format_first_name(first_name)]
    return name

def name_dict_to_str(name: dict) -> str:
    '''
    Concatenate the name information into a string.
    '''
    first = " ".join(name.get("first", []))
    von = " ".join(name.get("von", []))
    last = " ".join(name.get("last", []))
    jr = " ".join(name.get("jr", []))
    previous = first != ""
    if previous and von:
        von = f" {von}"
    if previous and last:
        last = f" {last}"
    if previous and jr:
        jr = f" {jr}"
    return f"{first}{von}{last}{jr}"

def config_special_names(config) -> dict[str, str]:
    '''
    Return the a dictionary mapping special names to their formatted version.
    '''
    special_names = config['special_names']
    for k, name in special_names.items():
        name = [w.strip() for w in name.split('|')]
        special_names[k] = name[0] if len(name) == 1 else name_dict_to_str(format_name_dict(splitname(", ".join(name[1:] + [name[0]]))))    
    return special_names

CONFIG = json.load(open('config_authfmt.json'))
CONFIG_SPECIAL_NAMES = config_special_names(CONFIG)

def format_name(name: str) -> str:
    '''
    Format the given string containing a person name.
    '''
    if name in CONFIG_SPECIAL_NAMES:
        return CONFIG_SPECIAL_NAMES[name]
    return name_dict_to_str(format_name_dict(splitname(name)))

def format_names(names: str) -> str:
    '''
    Format the given string containing people names.
    '''
    return ' and '.join(format_name(name) for name in split_names_to_strs(names))

def format_entry_names(entry):
    '''
    Format the names in the given entry.
    '''
    new_entry = entry.copy()
    if 'author' in new_entry:
        new_entry['author'] = format_names(new_entry['author'])
    if 'editor' in entry:
        new_entry['editor'] = format_names(entry['editor'])
    return new_entry

def format_entry(entry):
    '''
    Format the given entry.
    '''
    return format_entry_names(cleanup_record(entry))

def format_bib(path):
    '''
    Format the given bibliography file.
    '''
    # read bibliography
    with open(path, "r") as f:
        db = bp.load(f, _parser(customization=format_entry))

    # write the bibliography
    with open(path, "w") as f:
        bp.dump(db, f, _writer(sorted_entries=False))
   
if __name__ == "__main__":
    check_min_version()
    format_bib('krr.bib')
    format_bib('procs.bib')
    sys.exit(0)
