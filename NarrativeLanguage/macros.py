from Utils.iwhere import IWhere
from Utils.string_traversal import StringTraversal


class Macro(IWhere):

    def __init__(self, identifier, text, source):
        self.identifier = identifier
        self.text = text
        self.source = source

    def where(self) -> str:
        return "Macro '{}' declared in {}".format(
            self.identifier, self.source.where())

    def __repr__(self):
        return "#{} = {}".format(self.identifier, self.text)


class Macros:

    def __init__(self):
        self.macros = {}

    def find_and_remove_macro_definitions(self, source):
        control_characters_indices = set()
        traversal = StringTraversal(source.text)

        while True:
            _skip_to_pound(traversal)
            if traversal.at_end():
                break

            macro_start = traversal._pos
            if macro_start in control_characters_indices:
                # Ignore already found control character
                traversal.get_and_advance()  # Skip '#'
                continue

            # Check for control character '\#'
            prev_char = None if traversal._pos == 0 else \
                traversal.string[traversal._pos - 1]
            if prev_char == '\\':
                control_characters_indices.add(macro_start)
                continue

            # Extract identifier
            traversal.get_and_advance()  # Consume '#'
            identifier = _macro_identifier(source, macro_start, traversal)

            # Definitions are followed by '='
            _skip_whitespaces(traversal)
            if traversal.get() != '=':
                continue

            assert identifier not in self.macros, \
                "Macro '{}' already defined. {}".format(identifier, IWhere.msg([
                    "Existing: {}".format(self.macros[identifier].where()),
                    "New: {}".format(source.where())
                ]))

            # Extract macro value and remove its text
            traversal.get_and_advance()  # Consume '='
            _skip_whitespaces(traversal)
            text = _macro_text_and_remove(
                source, identifier, macro_start, traversal)

            # Define
            self.macros[identifier] = Macro(identifier, text, source)

            # Reset traversal pointer
            traversal._pos = 0

        source.text = traversal.string

    def replace_macros(self, source):
        control_characters_indices = set()
        traversal = StringTraversal(source.text)

        while True:
            _skip_to_pound(traversal)
            if traversal.at_end():
                break

            macro_start = traversal._pos
            if macro_start in control_characters_indices:
                # Ignore already found control character
                traversal.get_and_advance()  # Skip '#'
                continue

            # Check for control character '\#'
            prev_char = None if traversal._pos == 0 else \
                traversal.string[traversal._pos - 1]
            if prev_char == '\\':
                # Store and remove control character
                traversal.string = traversal.string[:macro_start - 1] + \
                    traversal.string[macro_start:]
                control_characters_indices.add(macro_start - 1)
                traversal._pos = 0  # Reset traversal pointer
                continue

            # Extract identifier
            traversal.get_and_advance()  # Consume '#'
            identifier = _macro_identifier(source, macro_start, traversal)

            assert identifier in self.macros, \
                "Unknown macro '{}'. {}".format(
                    identifier, IWhere.msg(source.where()))

            # Replace text
            macro = self.macros[identifier]
            traversal.string = traversal.string[:macro_start] + macro.text + \
                traversal.string[macro_start + len(identifier) + 1:]

            traversal._pos = 0  # Reset traversal pointer

        source.text = traversal.string

    def __repr__(self):
        return "MACROS"


def _macro_identifier(source, macro_start, traversal):
    assert _is_identifier_initial(traversal.get_and_advance()), \
        "Identifier expected to start with a letter or '_'. {}".format(
            IWhere.msg(source.where()))

    while _is_identifier(traversal.get()):
        traversal.get_and_advance()

    identifier = traversal.string[macro_start + 1:traversal._pos]
    return identifier


def _macro_text_and_remove(source, identifier, macro_start, traversal):
    assert traversal.get_and_advance() == '(', \
        "Error parsing macro '{}'. Expected '('. {}".format(
            identifier, IWhere.msg(source.where()))

    parenthesis_depth = 1
    text_start_index = traversal._pos
    while parenthesis_depth != 0 and not traversal.at_end():
        c = traversal.get_and_advance()
        if c == '(':
            parenthesis_depth += 1
        elif c == ')':
            parenthesis_depth -= 1

    assert parenthesis_depth == 0,\
        "Error parsing macro '{}'. Found EOS. {}".format(
            identifier, IWhere.msg(source.where()))

    # Extract text
    macro_text = traversal.string[text_start_index:traversal._pos - 1]

    # Remove from string
    traversal.string = traversal.string[:macro_start] + \
        traversal.string[traversal._pos:]

    return macro_text


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
