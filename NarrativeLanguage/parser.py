from NarrativeLanguage import expression, reporting
from NarrativeLanguage.token import TokenType


class TokenTraversal:

    def __init__(self, tokens):
        self.tokens = tokens

        self._pos = 0

    def at_end(self):
        return self.get().type == TokenType.EOF

    def previous(self):
        return self.tokens[self._pos - 1]

    def get(self):
        return self.tokens[self._pos]

    def get_and_advance(self):
        self._pos += 1
        return self.tokens[self._pos - 1]

    def match(self, token_type):
        if self.at_end():
            return False

        return self.get().type == token_type

    def match_and_if_so_advance(self, token_types):
        for token_type in token_types:
            if self.match(token_type):
                self.get_and_advance()
                return True

        return False


class Parser:

    EQUALITY_TOKENS = [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
    COMPARISON_TOKENS = [TokenType.LESS, TokenType.LESS_EQUAL,
                         TokenType.GREATER, TokenType.GREATER_EQUAL]
    TERM_TOKENS = [TokenType.PLUS, TokenType.MINUS]
    FACTOR_TOKENS = [TokenType.STAR, TokenType.SLASH]
    UNARY_TOKENS = [TokenType.MINUS, TokenType.BANG]
    LITERAL_TOKENS = [TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT]

    def __init__(self, tokens):
        self.tokens = tokens

        self._traversal = TokenTraversal(tokens)

    def parse(self):
        try:
            pos = self._traversal._pos
            return self._expression()
        except Exception as e:
            token = self.tokens[pos]
            reporting.error(
                token.line, "Parsing expression starting at {}".format(token))

            print(e)
            exit()

    def _expression(self):
        return self._equality()

    def _equality(self):
        expr = self._comparison()

        while self._traversal.match_and_if_so_advance(Parser.EQUALITY_TOKENS):
            operator = self._traversal.previous()
            right = self._comparison()
            expr = expression.BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self):
        expr = self._term()

        while self._traversal.match_and_if_so_advance(Parser.COMPARISON_TOKENS):
            operator = self._traversal.previous()
            right = self._term()
            expr = expression.BinaryExpr(expr, operator, right)

        return expr

    def _term(self):
        expr = self._factor()

        while self._traversal.match_and_if_so_advance(Parser.TERM_TOKENS):
            operator = self._traversal.previous()
            right = self._factor()
            expr = expression.BinaryExpr(expr, operator, right)

        return expr

    def _factor(self):
        expr = self._unary()

        while self._traversal.match_and_if_so_advance(Parser.FACTOR_TOKENS):
            operator = self._traversal.previous()
            right = self._unary()
            expr = expression.BinaryExpr(expr, operator, right)

        return expr

    def _unary(self):
        if self._traversal.match_and_if_so_advance(Parser.UNARY_TOKENS):
            operator = self._traversal.previous()
            expr = self._unary()
            return expression.UnaryExpr(operator, expr)

        return self._primary()

    def _primary(self):
        if self._traversal.match_and_if_so_advance(Parser.LITERAL_TOKENS):
            return expression.LiteralExpr(self._traversal.previous())

        if self._traversal.match_and_if_so_advance([TokenType.LEFT_PARENTHESIS]):
            expr = self._expression()
            assert self._traversal.match_and_if_so_advance([TokenType.RIGHT_PARENTHESIS]), \
                "Expected ')' after expression. At {}".format(
                    self._traversal.get())

            return expression.GroupingExpr(expr)

        raise Exception("Caused by {}".format(self._traversal.get()))
