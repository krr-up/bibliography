#!/usr/bin/env python3
'''
Script using the bibtexparser module to cleanup_record and pretty print our
bibliography.
'''

import sys
from io import StringIO
from argparse import ArgumentParser
from difflib import ndiff
from collections import OrderedDict

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
        if val.lower() == 'pages':
            x[val] = x[val].replace('--', '-')
    return x

def _parser():
    '''
    Return a configured bibtex parser.
    '''
    parser = BibTexParser()
    parser.interpolate_strings = False
    parser.customization = cleanup_record
    return parser

def _writer():
    '''
    Return a configured bibtex writer.
    '''
    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = ('ID',)
    writer.display_order = ['title', 'author', 'editor']
    return writer

def _fixdb(db):
    '''
    Currently sorts the strings in the database.
    '''
    db.strings = OrderedDict(sorted(db.strings.items()))
    return db

def format_bib(path):
    '''
    Format the given bibliography file.
    '''
    # read bibliography
    with open(path, "r") as f:
        db = _fixdb(bp.load(f, _parser()))

    # write the bibliography
    with open(path, "w") as f:
        bp.dump(db, f, _writer())

def check_bib(path):
    '''
    Check if the given bibliography is correctly formatted.
    '''
    # read bibliography
    with open(path, "r") as f:
        in_ = f.read()

    db = _fixdb(bp.loads(in_, _parser()))

    # write the bibliography
    out = StringIO()
    bp.dump(db, out, _writer())

    return [x for x in ndiff(in_.splitlines(), out.getvalue().splitlines()) if x[0] != ' ']


def run():
    '''
    Run the applications.
    '''
    check_min_version()

    parser = ArgumentParser(
        prog='bibfmt',
        description='Autoformat and check bibliography.')
    subparsers = parser.add_subparsers(
        metavar='command',
        dest='command',
        help='available subcommands',
        required=True)
    subparsers.add_parser(
        'check',
        help='check whether bibliography is correctly formatted')
    subparsers.add_parser(
        'format',
        help='format the bibliography')

    res = parser.parse_args()

    if res.command == "format":
        format_bib('krr.bib')
        format_bib('procs.bib')
        return 0

    assert res.command == "check"
    diff = check_bib('krr.bib') + check_bib('procs.bib')
    if diff:
        for x in diff:
            print(x, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(run())
