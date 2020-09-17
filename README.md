# Bibliography

> BibTeX bibliography files of all papers referenced by the group

## Installation

These instructions will make all BibTeX files in this repository available to BibTeX on your machine.

The following commands will first locate or create the directory where your TeX installation expects BibTeX files.
This repository will then be cloned to that location.

```sh
$ mkdir -p $(kpsewhich -var-value=TEXMFHOME)/bibtex/bib
$ cd "$_"
$ git clone https://github.com/krr-up/bibliography.git
```

If you prefer, you can clone the repository to another location and then create a symbolic link to the path TeX expects.

```sh
$ cd <preferred location>
$ git clone https://github.com/krr-up/bibliography.git
$ mkdir -p $(kpsewhich -var-value=TEXMFHOME)/bibtex/bib
$ ln -s <preferred location>/bibliography "$_"
```

Now, you can use the bibliography in your LaTeX file:

```latex
\bibliography{krr,procs}
```

## Contributing New BibTeX Entries

Before creating new BibTeX entries, **check whether they are already contained** in [krr.bib] or [procs.bib].
If not, add the new entries to [krr.bib] and **open a pull request.**
Please make sure that new BibTeX entries are **in line with the [guidelines](#guidelines-for-new-bibtex-entries)** below.
We will then review and merge your pull request in a timely fashion.

## Guidelines for New BibTeX Entries

### BibTeX Keys

BibTeX keys must **only contain ASCII characters.**
Depending on the number of authors, BibTeX keys should be chosen as follows:

- **1 author:** `[author][year][a-z]` (author’s *full* last name)

  > example: `lierler08a` for a 2008 paper by Y. Lierler
- **2 authors:** `[author 1][author 2][year][a-z]` (authors’ last names shortened to the *first 3 letters*)

  > example: `rantin06a` for a 2006 paper by S. Ranise and C. Tinelli
- **3+ authors:** `[author 1]...[author n][year][a-z]` (authors’ last names shortened to the *first 2 letters*)

  > example: `lirasm98a` for a 1998 paper by X. Liu and C. Ramakrishnan and S. Smolka

As the **`[year]`** field, use the *last 2 digits* of the publication year.

For the **`[a-z]`** suffix, `a` should be selected by default.
Should the resulting BibTeX key already exist, change the suffix to `b`, `c`, and so on until you obtain a **unique BibTeX key.**

For **proceedings** (mainly in [procs.bib]), use the following format instead:

- `[acronym][year]`

  > example: `lpnmr09` for *Proceedings of the Tenth International Conference on Logic Programming and Nonmonotonic Reasoning (LPNMR’09)*

### BibTeX Entries

Use `"` instead of `{` as the **field delimiter.**

> example:
> ```bibtex
> @InProceedings{marlyn07a,
>   author =	 "J. Marques-Silva and I. Lynce",
>   title =	 "Towards Robust {CNF} Encodings of Cardinality Constraints",
>   pages =	 "483-497",
>   crossref =	 "cp07"
> }
> ```

In the `author` and `editor` fields, **abbreviate first names** to the *first letter* and omit additional first names.
Spell out last names.

> example: `author = "M. Gebser and B. Kaufmann and T. Schaub"`

In the `title` field, **enclose capital letters** (other than the first letter) that must not be converted to lowercase letters by `{` and `}`.

> examples: `{SAT}`, `{P}etri Nets`

For proceedings with more than one reference, please use **`crossref`s**.

> example: `crossref = "aaai17"`

**Conference or workshop titles** should almost always start with “Proceedings of the …”

> example:
> ```bibtex
> @Proceedings{aaai17,
>   editor =	 "P. Satinder and S. Markovitch",
>   title =	 "Proceedings of the Thirty-first National Conference on Artificial Intelligence (AAAI'17)",
>   booktitle =	 "Proceedings of the Thirty-first National Conference on Artificial Intelligence (AAAI'17)",
>   publisher =	 "AAAI Press",
>   year =	 2017
> }
> ```

Don’t abbreviate **journal names.**

> example: `ACM Transactions on Computational Logic` but not `ACM Trans. on Comp. Log.`

Use the **strings** defined in [krr.bib] for journal names.

> example: `@STRING{lncs    = "Lecture Notes in Computer Science" }` for use in BibTex entries as `series =	 lncs`

Use LaTeX commands for **special characters** in all fields.

> example: `J. P{\"a}tynen` but not `J. Pätynen`

Use `-` rather than `--` for **hyphens** in the pages, volume, and number fields.
Don’t terminate field contents with `.`.
The bibliography style and BibTeX will sort it out uniformly.

> example: `pages =	 "203-208"`

Generally speaking, **never copy/paste** the contents of fields from PDF files because this might lead to issues with special characters (for instance, the ligature `ﬁ` might not be rendered at all by LaTeX and BibTeX).

[krr.bib]: lit.bib
[procs.bib]: procs.bib
