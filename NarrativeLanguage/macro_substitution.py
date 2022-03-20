from NarrativeLanguage.scanner import StringTraversal


def replace_macros(string):
    macros = {}
    control_characters_indices = set()

    # Find macro declarations
    traversal = StringTraversal(string)
    while True:
        _skip_to_pound(traversal)
        if traversal.at_end():
            break

        macro_start = traversal._pos
        assert traversal.get() == '#', "Expected '#'"

        # Skip control characters found
        if macro_start in control_characters_indices:
            traversal.get_and_advance()
            continue

        # Store control character
        prev_char = None if traversal._pos == 0 else \
            traversal.string[traversal._pos - 1]
        if prev_char == '\\':
            traversal.string = traversal.string[:macro_start - 1] + \
                traversal.string[macro_start:]
            control_characters_indices.add(macro_start - 1)
            traversal._pos = 0  # Reset pointer
            continue

        # Extract identifier
        traversal.get_and_advance()  # Consume '#'

        assert _is_identifier_initial(traversal.get_and_advance()), \
            "Identifier expected to start with a letter or '_'"
        while _is_identifier(traversal.get()):
            traversal.get_and_advance()

        identifier = traversal.string[macro_start + 1:traversal._pos]

        # Declarations are followed by a '='
        _skip_whitespaces(traversal)
        if traversal.get() == '=':
            _declare_macro_and_remove(
                macros, traversal, macro_start, identifier)
        else:
            _replace_macro(macros, traversal, macro_start, identifier)

        # Reset traversal pointer
        traversal._pos = 0

    return traversal.string


def _declare_macro_and_remove(macros, traversal, macro_start, identifier):
    # FORMAT
    # #IDENTIFIER = (TEXT)

    assert identifier not in macros, \
        "Macro '{}' already defined".format(identifier)

    # Check initial characters
    _skip_whitespaces(traversal)
    assert traversal.get_and_advance() == '=', "Expected '='"

    _skip_whitespaces(traversal)
    assert traversal.get_and_advance() == '(', "Expected '('"

    # Extract macro text
    parenthesis_depth = 1
    text_start_index = traversal._pos
    while parenthesis_depth != 0 and not traversal.at_end():
        c = traversal.get_and_advance()
        if c == '(':
            parenthesis_depth += 1
        elif c == ')':
            parenthesis_depth -= 1

    assert parenthesis_depth == 0, \
        "Found EOS while parsing macro '{}' declaration".format(identifier)

    macro_text = traversal.string[text_start_index: traversal._pos - 1]
    macros[identifier] = macro_text

    # Remove macro from string
    traversal.string = traversal.string[:macro_start] + \
        traversal.string[traversal._pos:]


def _replace_macro(macros, traversal, macro_start, identifier):
    # FORMAT
    # #IDENTIFIER

    assert identifier in macros, "Unknown macro '{}'".format(identifier)

    macro_text = macros[identifier]
    traversal.string = traversal.string[:macro_start] + macro_text + \
        traversal.string[macro_start + len(identifier) + 1:]


def _skip_to_pound(traversal):
    while traversal.get() != '#' and not traversal.at_end():
        traversal.get_and_advance()


def _skip_whitespaces(traversal):
    while traversal.get() in [' ', '\r', '\t', '\n']:
        traversal.get_and_advance()


def _is_identifier_initial(char):
    if char == StringTraversal.EOS:
        return False

    return char.isalpha() or char == '_'


def _is_identifier(char):
    return _is_identifier_initial(char) or char.isdigit()
