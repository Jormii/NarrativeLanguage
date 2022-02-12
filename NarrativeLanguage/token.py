from enum import auto, Enum


class TokenType(Enum):
    # Single character tokens
    LEFT_PARENTHESIS = auto()   # (
    RIGHT_PARENTHESIS = auto()  # )
    LEFT_BRACE = auto()         # {
    RIGHT_BRACE = auto()        # }
    PLUS = auto()               # +
    MINUS = auto()              # -
    STAR = auto()               # *
    SLASH = auto()              # /
    POUND = auto()              # '#'
    COMMA = auto()              # ,

    # One or two character tokens
    EQUAL = auto()              # =
    EQUAL_EQUAL = auto()        # ==
    BANG = auto()               # !
    BANG_EQUAL = auto()         # !=
    LESS = auto()               # <
    LESS_EQUAL = auto()         # <=
    GREATER = auto()            # >
    GREATER_EQUAL = auto()      # >=

    # Literals
    IDENTIFIER = auto()         # aA-zZ, 0-9, '_'
    STRING = auto()             # ""
    INTEGER = auto()            # INT i = 0
    FLOAT = auto()              # FLOAT f = 0.0

    # Keywords
    INT_KEYWORD = auto()        # INT
    FLOAT_KEYWORD = auto()      # FLOAT
    IF = auto()                 # IF
    ELIF = auto()               # ELIF
    ELSE = auto()               # ELSE
    AND = auto()                # AND
    OR = auto()                 # OR

    EOF = auto()


class Token:

    def __init__(self, type, lexeme, literal, line, column):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __repr__(self):
        return "Token [L{}, C{}]: {} | {} | {}".format(
            self.line,
            self.column,
            self.lexeme if self.lexeme else "_",
            self.literal,
            self.type
        )
