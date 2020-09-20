#!/usr/bin/env python3
'''
Script using the bibtexparser module to cleanup_record and pretty print our
bibliography.
'''

import os.path as op

import bibtexparser as bp
from bibtexparser.bibdatabase import BibDataStringExpression
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.latexenc import unicode_to_latex_map


def check_min_version():
    '''
    Ensure that a new enough version of bibtexparser is used.
    '''
    vers = bp.__version__.split('.')
    if (int(vers[0]), int(vers[1])) < (1, 2):
        raise RuntimeError('The script requires at least bibtexparser version 1.2.')

def is_ascii(x):
    '''
    Reurn true if the given string contains ascii symbols only.
    '''
    try:
        x.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

# Map from unicode symbols to latex expressions.
#
# The bibtexparser.latexenc module also maps some ascii characters to unicode
# symbols. Such characters are ignored in the map.
UNICODE_TO_LATEX = {key: value
                    for key, value in unicode_to_latex_map.items()
                    if not is_ascii(key)}


def apply_on_expression(x, f):
    '''
    Apply the function f for converting strings to bibtex expressions as
    returned by the bibtexparser module.
    '''
    if isinstance(x, str):
        return f(x)
    if isinstance(x, BibDataStringExpression):
        x.apply_on_strings(f)
    return x

def cleanup_expression(x):
    '''
    Convert the given string containing unicode symbols into a string with
    latex escapes only.
    '''
    ret = []
    for char in x:
        if char in (' ', '{', '}'):
            ret.append(char)
        else:
            ret.append(UNICODE_TO_LATEX.get(char, char))
    return ''.join(ret)

def cleanup_record(x):
    '''
    Cleanup a record as returned by the bibtexparser module.
    '''
    for val in x:
        if val in ('ID',):
            continue
        x[val] = apply_on_expression(x[val], cleanup_expression)
    return x

def format_bib(path):
    '''
    Format the given bibliography file.
    '''
    # read bibliography
    parser = BibTexParser()
    parser.interpolate_strings = False
    parser.customization = cleanup_record
    with open(path, "r") as f:
        db = bp.load(f, parser)
        db.expand_string = lambda name: name


    # write the bibliography
    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = None
    writer.display_order = ['title', 'author', 'editor']

    path, ext = op.splitext(path)

    with open(f"{path}_fmt{ext}", "w") as f:
        bp.dump(db, f, writer)

if __name__ == "__main__":
    check_min_version()
    format_bib('krr.bib')
    format_bib('procs.bib')
