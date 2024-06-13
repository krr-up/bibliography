import bibtexparser as bp


def split_latex_to_sections(
    latex_string: str, strict_mode=True
) -> tuple[list[list[str]], list[list[int]]]:
    """
    Split the given latex string into sections.
    Returns two lists of lists. Each list on the first of those two lists contains the words of a section.
    Each list on the second of those two lists contains the case of each word in the corresponding section: 1 = uppercase, 0 = lowercase, -1 = caseless.
    """
    whitespace = set(" ~\r\n\t")

    # We'll iterate over the input once, dividing it into a list of words for
    # each comma-separated section. We'll also calculate the case of each word
    # as we work.
    sections = [[]]  # Sections of the name.
    cases = [[]]  # 1 = uppercase, 0 = lowercase, -1 = caseless.
    word = []  # Current word.
    case = -1  # Case of the current word.
    level = 0  # Current brace level.
    bracestart = False  # Will the next character be the first within a brace?
    controlseq = True  # Are we currently processing a control sequence?
    specialchar = None  # Are we currently processing a special character?

    # Using an iterator allows us to deal with escapes in a simple manner.
    nameiter = iter(latex_string)
    for char in nameiter:
        # An escape.
        if char == "\\":
            escaped = next(nameiter)

            # BibTeX doesn't allow whitespace escaping. Copy the slash and fall
            # through to the normal case to handle the whitespace.
            if escaped in whitespace:
                word.append(char)
                char = escaped
            else:
                # Is this the first character in a brace?
                if bracestart:
                    bracestart = False
                    controlseq = escaped.isalpha()
                    specialchar = True

                # Can we use it to determine the case?
                elif (case == -1) and escaped.isalpha():
                    if escaped.isupper():
                        case = 1
                    else:
                        case = 0

                # Copy the escape to the current word and go to the next
                # character in the input.
                word.append(char)
                word.append(escaped)
                continue

        # Start of a braced expression.
        if char == "{":
            level += 1
            word.append(char)
            bracestart = True
            controlseq = False
            specialchar = False
            continue

        # All the below cases imply this (and don't test its previous value).
        bracestart = False

        # End of a braced expression.
        if char == "}":
            # Check and reduce the level.
            if level:
                level -= 1
            else:
                if strict_mode:
                    raise bp.customization.InvalidName(
                        "Unmatched closing brace in name {{{0}}}.".format(name)
                    )
                word.insert(0, "{")

            # Update the state, append the character, and move on.
            controlseq = False
            specialchar = False
            word.append(char)
            continue

        # Inside a braced expression.
        if level:
            # Is this the end of a control sequence?
            if controlseq:
                if not char.isalpha():
                    controlseq = False

            # If it's a special character, can we use it for a case?
            elif specialchar:
                if (case == -1) and char.isalpha():
                    if char.isupper():
                        case = 1
                    else:
                        case = 0

            # Append the character and move on.
            word.append(char)
            continue

        # End of a word.
        # NB. we know we're not in a brace here due to the previous case.
        if char == "," or char in whitespace:
            # Don't add empty words due to repeated whitespace.
            if word:
                sections[-1].append("".join(word))
                word = []
                cases[-1].append(case)
                case = -1
                controlseq = False
                specialchar = False

            # End of a section.
            if char == ",":
                if len(sections) < 3:
                    sections.append([])
                    cases.append([])
                elif strict_mode:
                    raise bp.customization.InvalidName(
                        "Too many commas in the name {{{0}}}.".format(name)
                    )
            continue

        # Regular character.
        word.append(char)
        if (case == -1) and char.isalpha():
            if char.isupper():
                case = 1
            else:
                case = 0

    # Unterminated brace?
    if level:
        if strict_mode:
            raise bp.customization.InvalidName(
                "Unterminated opening brace in the name {{{0}}}.".format(name)
            )
        while level:
            word.append("}")
            level -= 1

    # Handle the final word.
    if word:
        sections[-1].append("".join(word))
        cases[-1].append(case)

    return sections, cases


def splitname(name, strict_mode=True):
    """
    Break a name into its constituent parts: First, von, Last, and Jr.

    :param string name: a string containing a single name
    :param Boolean strict_mode: whether to use strict mode
    :returns: dictionary of constituent parts
    :raises `customization.InvalidName`: If an invalid name is given and
                                         ``strict_mode = True``.

    In BibTeX, a name can be represented in any of three forms:
        * First von Last
        * von Last, First
        * von Last, Jr, First

    This function attempts to split a given name into its four parts. The
    returned dictionary has keys of ``first``, ``last``, ``von`` and ``jr``.
    Each value is a list of the words making up that part; this may be an empty
    list.  If the input has no non-whitespace characters, a blank dictionary is
    returned.

    It is capable of detecting some errors with the input name. If the
    ``strict_mode`` parameter is ``True``, which is the default, this results in
    a :class:`customization.InvalidName` exception being raised. If it is
    ``False``, the function continues, working around the error as best it can.
    The errors that can be detected are listed below along with the handling
    for non-strict mode:

        * Name finishes with a trailing comma: delete the comma
        * Too many parts (e.g., von Last, Jr, First, Error): merge extra parts
          into Last. The second part is merged into First if it is an initial.
        * Unterminated opening brace: add closing brace to end of input
        * Unmatched closing brace: add opening brace at start of word

    """
    # Modified from the bibtexparser.customization.splitname function to merge into Last instead of First.
    # The ``von`` part is ignored unless commans are used as separators. Note that ``von`` part colides with uncapitalized parts of the last name.
    # Useful references:
    # http://maverick.inria.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html#names
    # http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf

    # Group names of exceptional cases.
    # if " ".join(name.split()) in data.GROUPING_NAMES:
    #     name_parts =  [word.strip() for word in data.GROUPING_NAMES[name].split("|")]
    #     name_parts = name_parts[1:] + name_parts[:1]
    #     name = ",".join(name_parts)

    sections, cases = split_latex_to_sections(name, strict_mode)

    # Get rid of trailing sections.
    if not sections[-1]:
        # Trailing comma?
        if (len(sections) > 1) and strict_mode:
            raise bp.customization.InvalidName(
                "Trailing comma at end of name {{{0}}}.".format(name)
            )
        sections.pop(-1)
        cases.pop(-1)

    # No non-whitespace input.
    if not sections or not any(bool(section) for section in sections):
        return {}

    # Initialise the output dictionary.
    parts = {"first": [], "last": [], "von": [], "jr": []}

    # Form 1: "First von Last"
    # print(f"{sections=}")
    # print(cases)
    if len(sections) == 1:
        p0 = sections[0]
        cases = cases[0]
        # One word only: last cannot be empty.
        if len(p0) == 1:
            parts["last"] = p0

        # Two words: must be first and last.
        elif len(p0) == 2:
            parts["first"] = p0[:1]
            parts["last"] = p0[1:]

        # Need to use the cases to figure it out.
        elif len(p0) > 2 and p0[1][1] == ".":
            parts["first"] = p0[:2]
            parts["last"] = p0[2:]
        else:
            num_capitals = sum(cases)
            if num_capitals > 2:
                capital_position = [i for i, e in enumerate(cases) if e]
                third_to_last_captilized = capital_position[-3]
                second_to_last_captilized = capital_position[-2]
                parts["first"] = p0[: third_to_last_captilized + 1]
                parts["von"] = p0[
                    third_to_last_captilized + 1 : second_to_last_captilized
                ]
                parts["last"] = p0[second_to_last_captilized:]
            else:
                parts["first"] = p0[:1]
                parts["last"] = p0[1:]

    # Form 2 ("von Last, First") or 3 ("von Last, jr, First")
    else:
        # As long as there is content in the first name partition, use it as-is.
        first = sections[-1]
        if first and first[0]:
            parts["first"] = first

        # And again with the jr part.
        if len(sections) == 3:
            jr = sections[-2]
            if jr and jr[0]:
                parts["jr"] = jr

        # Last name cannot be empty; if there is only one word in the first
        # partition, we have to use it for the last name.
        last = sections[0]
        if len(last) == 1:
            parts["last"] = last

        # Have to look at the cases to figure it out.
        else:
            lcases = cases[0]

            # At least one lowercase: von is the longest sequence of whitespace
            # separated words whose last word does not start with an uppercase
            # word, and last is the rest.
            if 0 in lcases:
                split = len(lcases) - lcases[::-1].index(0)
                if split == len(lcases):
                    split = 0  # Last cannot be empty.
                parts["von"] = sections[0][:split]
                parts["last"] = sections[0][split:]

            # All uppercase => all last.
            else:
                parts["last"] = sections[0]

    # Done.
    return parts
