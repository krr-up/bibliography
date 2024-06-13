I have been using a modified version of the ```bibfmt``` program to further automatize the formatting of the BibTeX entries copied from DBLP.
- It abbreviates first names: Roland Kaminski becomes R. Kaminski.
- It generates BibTeX keys from the author names and the year using the bibliography conventions
- It replaces journal names by their corresponding BibTeX strings
- It finds crossrefs in the procs.bib file and uses them for crossref field
- It flags repeated entries

You can try it out by running the following command in the root directory of the repository:
```bash
cp krr-test.bib krr.bib && python bibfmt.py entries && git diff --no-index -w krr-test.bib krr.bib
```
It does not remove repeated entries, it only flags them. They can be removed by running ```python bibfmt.py clean```.
```
python bibfmt.py clean && git diff --no-index -w krr-test.bib krr.bib
```
It keeps the entries in their original order, so you can see them before committing the changes. It does well with most names.
In particular, all the names composed of two words. For names with more than two words the splitting of first/last names is in general ambiguous, so you may need to fix some of them manually: ```Juan Carlos Nieves``` should be parsed as ```{Juan Carlos} Nieves``` and ```Manuel Ojeda Aciego``` as ```Manuel {Ojeda Aciego}```. 

You can add the brackets to disambiguate. By default it parses the last two words as part of the last name unless the second is an abbreviation, ```Sheila A. McIlraith``` is parsed as ```{Sheila A.} McIlraith```. A list of know exceptions is kept so no need to disambiguate them. It would become crazy the day the King of Spain decides to write a paper about ASP: ```Felipe Juan Pablo Alfonso de Todos los Santos de Borb{\'o}n y Grecia``` should be parsed as ```{Felipe Juan Pablo Alfonso de Todos los Santos} {de Borb{\'o}n y Grecia}```. You should still do ```python bibfmt.py format``` before committing.

Somebody may find it useful.