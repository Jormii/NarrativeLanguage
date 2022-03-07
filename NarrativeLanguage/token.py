from enum import auto, Enum


class TokenType(Enum):
    # Single character tokens
    LEFT_PARENTHESIS = auto()   # (
    RIGHT_PARENTHESIS = auto()  # )
    LEFT_BRACE = auto()         # {
    RIGHT_BRACE = auto()        # }
    LEFT_SQR_BRACKET = auto()   # [
    RIGHT_SQR_BRACKET = auto()  # ]
    PLUS = auto()               # +
    MINUS = auto()              # -
    STAR = auto()               # *
    SLASH = auto()              # /
    POUND = auto()              # '#'
    COMMA = auto()              # ,
    SEMICOLON = auto()          # ;

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
    STRING = auto()             # s = ""
    INTEGER = auto()            # i = 0
    FLOAT = auto()              # f = 0.0

    # Keywords
    GLOBAL = auto()             # GLOBAL var
    STORE = auto()              # STORE var
    DISPLAY = auto()            # DISPLAY
    HIDE = auto()               # HIDE
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

    def copy(self):
        if self.literal is None:
            literal = self.literal
        else:
            t = type(self.literal)
            literal = t(self.literal)

        return Token(self.type, str(self.lexeme), literal,
                     self.line, self.column)

    @staticmethod
    def empty():
        return Token(None, None, None, None, None)

    def __repr__(self):
        return "Token [L{}, C{}]: {} | {} | {}".format(
            self.line,
            self.column,
            self.lexeme if self.lexeme else "_",
            self.literal,
            self.type
        )
