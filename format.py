#!/usr/bin/env python3

import bibtexparser as bp
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import homogenize_latex_encoding

def format_bib():
    parser = BibTexParser()
    # replace unicode characters with special charactars
    parser.customization = homogenize_latex_encoding
    with open("krr.bib", "r") as f:
        db = bp.load(f, parser)

    # write the bibliography
    # TODO: more customization is necessary
    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = None
    writer.display_order = ['title', 'author']
    with open("krr_fmt.bib", "w") as f:
        bp.dump(db, f, writer)

if __name__ == "__main__":
    format_bib()
