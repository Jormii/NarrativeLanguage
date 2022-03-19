from NarrativeLanguage.scanner import StringTraversal


class Macro:

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


def replace_macros(string):
    macros = {}
    in_order = []

    # Find macro declarations
    traversal = StringTraversal(string)
    while True:
        _skip_to_pound(traversal)
        if traversal.at_end():
            break

        macro_start = traversal._pos
        assert traversal.get_and_advance() == '#', "Expected '#'"

        while _is_identifier(traversal.get()):
            traversal.get_and_advance()
        identifier = traversal.string[macro_start + 1:traversal._pos]

        # Declarations are followed by a '='
        _skip_whitespaces(traversal)
        if traversal.get() != '=':
            continue

        traversal.get_and_advance()     # Consume '='

        # Get text
        # Make sure the first character is a '('
        _skip_whitespaces(traversal)
        assert traversal.get_and_advance() == '(', "Expected '('"

        macro_decl_start = traversal._pos
        parenthesis_depth = 1
        while parenthesis_depth != 0 and not traversal.at_end():
            c = traversal.get_and_advance()
            if c == '(':
                parenthesis_depth += 1
            elif c == ')':
                parenthesis_depth -= 1

        macro_decl_end = traversal._pos
        text = traversal.string[macro_decl_start:macro_decl_end - 1]

        # Update variables
        assert identifier not in macros, "Macro '{}' already defined"

        macros[identifier] = Macro(text, macro_start, macro_decl_end)
        in_order.append(identifier)

    # Remove macros from text
    replaced = str(string)
    for identifier in reversed(in_order):
        macro = macros[identifier]
        replaced = replaced[:macro.start] + replaced[macro.end:]

    # Replace in text
    for identifier, macro in macros.items():
        str_to_find = "#{}".format(identifier)
        length = len(str_to_find)

        start_index = replaced.find(str_to_find)
        while start_index != -1:
            replaced = replaced[:start_index] + \
                macro.text + replaced[start_index + length:]
            start_index = replaced.find(str_to_find)

    return replaced


def _skip_to_pound(traversal):
    while traversal.get() != '#' and not traversal.at_end():
        traversal.get_and_advance()


def _skip_whitespaces(traversal):
    while traversal.get() in [' ', '\r', '\t', '\n']:
        traversal.get_and_advance()


def _is_identifier(char):
    if char == StringTraversal.EOS:
        return False

    return char.isdigit() or char.isalpha() or char == '_'
