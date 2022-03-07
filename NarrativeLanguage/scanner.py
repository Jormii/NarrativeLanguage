from NarrativeLanguage import token, reporting


class StringTraversal:

    EOS = -1

    def __init__(self, string):
        self.string = string

        self._pos = 0

    def current_index(self):
        return self._pos

    def at_end(self):
        return self._pos >= len(self.string)

    def get(self):
        if self.at_end():
            return StringTraversal.EOS

        return self.string[self._pos]

    def peek(self):
        self._pos += 1
        c = self.get()
        self._pos -= 1

        return c

    def get_and_advance(self):
        if self.at_end():
            return StringTraversal.EOS

        self._pos += 1
        return self.string[self._pos - 1]

    def match_and_if_so_advance(self, char):
        if self.at_end():
            return False

        c = self.get()
        match = c == char
        if match:
            self.get_and_advance()

        return match


class Scanner:

    WHITESPACES = {' ', '\r', '\t', '\n'}

    SINGLE_TOKENS_MAPPING = {
        '(': token.TokenType.LEFT_PARENTHESIS,
        ')': token.TokenType.RIGHT_PARENTHESIS,
        '{': token.TokenType.LEFT_BRACE,
        '}': token.TokenType.RIGHT_BRACE,
        '[': token.TokenType.LEFT_SQR_BRACKET,
        ']': token.TokenType.RIGHT_SQR_BRACKET,
        '+': token.TokenType.PLUS,
        '-': token.TokenType.MINUS,
        '*': token.TokenType.STAR,
        '/': token.TokenType.SLASH,
        '#': token.TokenType.POUND,
        ',': token.TokenType.COMMA,
        ';': token.TokenType.SEMICOLON
    }

    SINGLE_OR_PAIR_TOKENS_MAPPING = {
        '=': (token.TokenType.EQUAL, token.TokenType.EQUAL_EQUAL),
        '!': (token.TokenType.BANG, token.TokenType.BANG_EQUAL),
        '<': (token.TokenType.LESS, token.TokenType.LESS_EQUAL),
        '>': (token.TokenType.GREATER, token.TokenType.GREATER_EQUAL)
    }

    KEYWORDS_MAPPING = {
        "GLOBAL": token.TokenType.GLOBAL,
        "STORE": token.TokenType.STORE,
        "DISPLAY": token.TokenType.DISPLAY,
        "HIDE": token.TokenType.HIDE,
        "IF": token.TokenType.IF,
        "ELIF": token.TokenType.ELIF,
        "ELSE": token.TokenType.ELSE,
        "AND": token.TokenType.AND,
        "OR": token.TokenType.OR
    }

    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []

        self._line = 1
        self._column = 1
        self._start = 0     # Index a token starts at
        self._traversal = StringTraversal(source_code)

    def scan(self):
        while not self._traversal.at_end():
            self._start = self._traversal.current_index()
            self._scan_token()

        eof_token = token.Token(token.TokenType.EOF, "",
                                None, self._line, self._column)
        self.tokens.append(eof_token)

    def _scan_token(self):
        c = self._traversal.get_and_advance()
        if c in Scanner.WHITESPACES:
            if c == '\n':
                self._line += 1
                self._column = 1
            else:
                self._column += 1
        elif c in Scanner.SINGLE_TOKENS_MAPPING:
            token_type = Scanner.SINGLE_TOKENS_MAPPING[c]
            self._add_simple_token(token_type)
        elif c in Scanner.SINGLE_OR_PAIR_TOKENS_MAPPING:
            match = self._traversal.match_and_if_so_advance('=')
            token_type = Scanner.SINGLE_OR_PAIR_TOKENS_MAPPING[c][match]
            self._add_simple_token(token_type)
        elif self._is_alpha(c) or c == '_':
            self._scan_identifier()
            identifier = self.tokens[-1]
            if identifier.lexeme in Scanner.KEYWORDS_MAPPING:
                identifier.type = Scanner.KEYWORDS_MAPPING[identifier.lexeme]
        elif c == '\"':
            self._scan_string()
        elif c.isdigit():
            self._scan_number()
        else:
            reporting.error(self._line, "Unexpected character '{}'".format(c))
            exit()

    def _scan_identifier(self):
        while self._is_identifier(self._traversal.get()):
            self._traversal.get_and_advance()

        self._add_simple_token(token.TokenType.IDENTIFIER)

    def _scan_string(self):
        while not self._traversal.at_end() and self._traversal.get() != '\"':
            if self._traversal.get() == '\n':
                self._line += 1
                self._column = 1

            if self._traversal.get() == '\\':
                # Skip an additional character if a control character is found
                self._traversal.get_and_advance()

            self._traversal.get_and_advance()

        if self._traversal.at_end():
            substring = self.source_code[self._start:]
            reporting.error(
                self._line, "Unterminated string: {}".format(substring))

        self._traversal.get_and_advance()    # Consume closing '\"'

        value = self.source_code[
            self._start + 1: self._traversal.current_index() - 1]
        self._add_token(token.TokenType.STRING, value)

    def _scan_number(self):
        while self._is_digit(self._traversal.get()):
            self._traversal.get_and_advance()

        is_float = self._traversal.get() == '.'
        if is_float and self._is_digit(self._traversal.peek()):
            self._traversal.get_and_advance()    # Consume '.'

            while self._is_digit(self._traversal.get()):
                self._traversal.get_and_advance()

        substring = self.source_code[
            self._start:self._traversal.current_index()]
        if is_float:
            token_type = token.TokenType.FLOAT
            value = float(substring)
        else:
            token_type = token.TokenType.INTEGER
            value = int(substring)

        self._add_token(token_type, value)

    def _add_simple_token(self, token_type):
        self._add_token(token_type, None)

    def _add_token(self, token_type, literal):
        lexeme = self.source_code[self._start: self._traversal.current_index()]
        column = self._column
        new_token = token.Token(
            token_type, lexeme, literal, self._line, column)

        self.tokens.append(new_token)
        self._column += len(lexeme)

    def _is_alpha(self, c):
        if c == StringTraversal.EOS:
            return False

        return c.isalpha()

    def _is_digit(self, c):
        if c == StringTraversal.EOS:
            return False

        return c.isdigit()

    def _is_identifier(self, c):
        return self._is_alpha(c) or self._is_digit(c) or c == '_'
