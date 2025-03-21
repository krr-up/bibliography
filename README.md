# Bibliography

> BibTeX bibliography files of all papers referenced by the group

## Installation

These instructions will make all BibTeX files in this repository available to
BibTeX on your machine.

The following commands will first locate or create the directory where your TeX
installation expects BibTeX files. This repository will then be cloned to that
location.

```sh
mkdir -p $(kpsewhich -var-value=TEXMFHOME)/bibtex/bib
cd "$_"
git clone https://github.com/krr-up/bibliography.git
```

If you prefer, you can clone the repository to another location and then create
a symbolic link to the path TeX expects.

```sh
cd <preferred location>
git clone https://github.com/krr-up/bibliography.git
mkdir -p $(kpsewhich -var-value=TEXMFHOME)/bibtex/bib
ln -s <preferred location>/bibliography "$_"
```

Now, you can use the bibliography in your LaTeX file:

```latex
\bibliography{krr,procs}
```

## Contributing New BibTeX Entries

Before creating new BibTeX entries, **check whether they are already
contained** in [krr.bib] or [procs.bib]. If not, add the new entries to
[krr.bib] and **open a pull request.** Please make sure that new BibTeX entries
are **in line with the [guidelines](#guidelines-for-new-bibtex-entries)**
below. We will then review and merge your pull request in a timely fashion.

## Guidelines for New BibTeX Entries

### BibTeX Keys

BibTeX keys must **only contain ASCII characters.**
Depending on the number of authors, BibTeX keys should be chosen as follows:

- **1 author:** `[author][year][a-z]` (author’s *full* last name)

  > example: `lierler08a` for a 2008 paper by Y. Lierler
- **2 authors:** `[author 1][author 2][year][a-z]` (authors’ last names
  shortened to the *first 3 letters*)

  > example: `rantin06a` for a 2006 paper by S. Ranise and C. Tinelli
- **3+ authors:** `[author 1]...[author n][year][a-z]` (authors’ last names
  shortened to the *first 2 letters*)

  > example: `lirasm98a` for a 1998 paper by X. Liu and C. Ramakrishnan and S.
  > Smolka

As the **`[year]`** field, use the *last 2 digits* of the publication year.

For the **`[a-z]`** suffix, `a` should be selected by default. Should the
resulting BibTeX key already exist, change the suffix to `b`, `c`, and so on
until you obtain a **unique BibTeX key.**

For **proceedings** (mainly in [procs.bib]), use the following format instead:

- `[acronym][year]`

  > example: `lpnmr09` for *Proceedings of the Tenth International Conference
  > on Logic Programming and Nonmonotonic Reasoning (LPNMR’09)*

### BibTeX Entries

Use `{` instead of `"` as the **field delimiter.**

> example:
>
> ```bibtex
> @inproceedings{marlyn07a,
>   author = {J. Marques-Silva and I. Lynce},
>   title = {Towards Robust {CNF} Encodings of Cardinality Constraints},
>   pages = {483-497},
>   crossref = {cp07}
> }
> ```

In the `author` and `editor` fields, **abbreviate first names** to the *first
letter* and omit additional first names. Spell out last names. See
[Autoformatting](#autoformatting) for a script to handle common cases.

> example: `author = {M. Gebser and J. von Neumann and A. {V}an Gelder and M. {D}'\relax Agostino and M. {Ojeda Aciego}}`

When a name consists of more than two words, refer to the [BibTex
documentation][bibtex].

> examples:
>
> - `Juan Carlos Nieves`           -> `J. Nieves`
> - `Manuel {Ojeda Aciego}`        -> `M. {Ojeda Aciego}`
> - `John von Neumann`             -> `J. von Neumann`
> - `Allen {V}an Gelder`           -> `A. {V}an Gelder`
> - `Luis Fari{\~n}as del Cerro` -> `L. {Fari{\~n}as del Cerro}`
> - `Marcello D'Agostino`          -> `M. {D}'\relax Agostino`

In the `title` field, **enclose capital letters** (other than the first letter)
that must not be converted to lowercase letters by `{` and `}`.

> examples: `{SAT}`, `{P}etri Nets`

For proceedings with more than one reference, please use **`crossref`s**.

> example: `crossref = {aaai17}`

**Conference or workshop titles** should almost always start with “Proceedings
of the …”

> example:
>
> ```bibtex
> @proceedings{aaai17,
>   editor = {P. Satinder and S. Markovitch},
>   title = {Proceedings of the Thirty-first National Conference on Artificial Intelligence (AAAI'17)},
>   booktitle = {Proceedings of the Thirty-first National Conference on Artificial Intelligence (AAAI'17)},
>   publisher = {AAAI Press},
>   year = {2017}
> }
> ```

Don’t abbreviate **journal names.**

> example: `ACM Transactions on Computational Logic` but not `ACM Trans. on
> Comp. Log.`

Use the **strings** defined in [krr.bib] for journal names.

> example: `@string{lncs = {Lecture Notes in Computer Science}}` for use in
> BibTex entries as `series = lncs`

Use LaTeX commands for **special characters** in all fields putting (a single pair of) braces around the command.

> example: `J. P{\"a}tynen` but neither `J. P{\"{a}}tynen`, `J. Pätynen`, `J. P\"atynen`, `J. P\"{a}tynen`, nor `J. P{{\"a}}tynen`.

Use `-` rather than `--` for **hyphens** in the pages, volume, and number fields.
Don’t terminate field contents with `.`.
The bibliography style and BibTeX will sort it out uniformly.

> example: `pages = {203-208}`

### Autoformatting

Always run the [bibfmt] script to format entries:

```sh
python bibfmt.py format-names
# check result!
python bibfmt.py format
# check result!
```

The `format-names` subcommand tries to autoformat names in the bibliography.
**Always** check the result of the script. To facilitate the editing process,
the script does not sort entries and should be followed by subcommand `format`.

The `format` subcommand takes care of sorting, indenting, replacing Unicode
characters, and spacing. Nevertheless, **always** check the result of the
script. Especially, when pasting contents from external sources (like titles of
PDFs) make sure that special characters like ligatures were replaced correctly.

The script requires at least Python 3.10 and the [bibtexparser] 1.3 module.
It is quite easy to setup with anaconda:

```sh
# install anaconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# setup environment
conda create -n bib python=3.10 pip
conda activate bib
pip install 'bibtexparser>=1.3,<2.0'

# run bibfmt
conda activate bib
```

[krr.bib]: krr.bib
[procs.bib]: procs.bib
[bibfmt]: bibfmt.py
[bibtexparser]: https://github.com/sciunto-org/python-bibtexparser
[bibtex]: https://us.mirrors.cicku.me/ctan/info/bibtex/tamethebeast/ttb_en.pdf
