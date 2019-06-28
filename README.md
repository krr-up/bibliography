# Bibliography

> BibTeX bibliography files of all papers referenced by the group

## Usage

The bibliography is meant to be used as a **Git submodule** within your paper repository.
Conceptually, this means that Git will maintain a copy of the bibliography within a subdirectory of your own repository (we suggest `includes/bibliography`).

Git submodules are always **locked to a specific commit.**
In other words, the bibliography **won’t automatically update itself,** even when pulling in the latest changes of your paper repository.
You’ll have to **manually update the bibliography** whenever necessary.

On another note, **never edit the content of the submodule directly,** that is, within `includes/bibliography`.
If you need new entries added, clone the bibliography to a location outside of your paper repository and contribute from there.

Read more about Git submodules on the [GitHub Blog][github-blog-git-submodules] and the in [Pro Git book][pro-git-book-git-submodules].

### Adding the Bibliography to your Paper Repository

**Add the bibliography as a submodule** to your paper repository as follows:
```sh
$ git submodule add ../bibliography includes/bibliography
```
(Replace `../bibliography` with `https://github.com/krr-up/bibliography` if your repository is hosted outside of the [`krr-up` organization][krr-up].)

Next, **commit and push** the changes to make the submodule available to your coworkers.
After your coworkers have pulled the change, they will need to **execute the following command:**
```sh
$ git submodule update --init --recursive
```

The bibliography will now stay at the latest state of the `master` branch **at the time of adding the submodule** unless manually updated later on.

### Using the Bibliography with LaTeX

By default, the LaTeX toolchain won’t attempt to look for the bibliography within `includes/bibliography`.
If you build your paper with [`latexmk`][latexmk] (we can only recommend that), this can be easily solved.
Simply copy the [`.latexmkrc`][.latexmkrc] file to the top level of your repository, and LaTeX will automatically find the bibliography if you just run `latexmk`:
```sh
$ latexmk -pdf paper.tex
```

If you do not use `latexmk`, you need to set the following environment variables in your `.bashrc` or LaTeX IDE instead:
```sh
export BIBINPUTS="./include//:"
export BSTINPUTS="./include//:"
export TEXINPUTS="./include//:"
```

### Updating the Bibliography in your Paper Repository

You can **bring the latest bibliography updates to your paper repository** as follows:

```sh
$ cd includes/bibliography
$ git fetch
$ git reset --hard origin/master
$ cd ../..
$ git add includes/bibliography
$ git commit -m "Update bibliography"
$ git push
```

Finally, keep in mind that you need to run
```sh
$ git submodule update --init --recursive
```
**every time one of the following happens:**
- You **clone** your paper repository from scratch.
- Someone else **updates the bibliography** to a newer version.
- Files in `includes/bibliography` are **missing** or LaTeX complains about them.
- `git status` tells you `modified: includes/bibliography (new commits)` and you didn’t expect this.
- Someone else adds a **new submodule** to your paper repository.

## Contributing New BibTeX Entries

Before creating new BibTeX entries, **check whether they are already contained** in [lit.bib], [procs.bib], or [akku.bib].
If not, add the new entries to [lit.bib] and **open a pull request.**
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

Use the **strings** defined in [lit.bib] for journal names.

> example: `@STRING{lncs    = "Lecture Notes in Computer Science" }` for use in BibTex entries as `series =	 lncs`

Use LaTeX commands for **special characters** in all fields.

> example: `J. P{\"a}tynen` but not `J. Pätynen`

Use `-` rather than `--` for **hyphens** in the pages, volume, and number fields.
Don’t terminate field contents with `.`.
The bibliography style and BibTeX will sort it out uniformly.

> example: `pages =	 "203-208"`

Generally speaking, **never copy/paste** the contents of fields from PDF files because this might lead to issues with special characters (for instance, the ligature `ﬁ` might not be rendered at all by LaTeX and BibTeX).

[akku.bib]: akku.bib
[lit.bib]: lit.bib
[procs.bib]: procs.bib
[.latexmkrc]: .latexmkrc
[krr-up]: https://github.com/krr-up
[latexmk]: https://mg.readthedocs.io/latexmk.html
[github-blog-git-submodules]: https://github.blog/2016-02-01-working-with-submodules/
[pro-git-book-git-submodules]: https://git-scm.com/book/en/v2/Git-Tools-Submodules
