from NarrativeLanguage import expression, statement, reporting
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
        self.statements = []

        self._traversal = TokenTraversal(tokens)

    def parse(self):
        try:
            while not self._traversal.at_end():
                pos = self._traversal._pos
                stmt = self._declaration()
                self.statements.append(stmt)
        except Exception as e:
            token = self.tokens[pos]
            reporting.error(
                token.line, "Parsing statement starting at {}".format(token))

            print(e)
            exit()

    def _declaration(self):
        if self._traversal.match_and_if_so_advance([TokenType.INT_KEYWORD, TokenType.FLOAT_KEYWORD]):
            return self._variable_declaration()
        else:
            return self._statement()

    def _variable_declaration(self):
        type_token = self._traversal.previous()
        identifier_token = self._traversal.get_and_advance()
        initializer_expr = None
        if self._traversal.match_and_if_so_advance([TokenType.EQUAL]):
            initializer_expr = self._expression()

        return statement.VariableStmt(type_token, identifier_token, initializer_expr)

    def _statement(self):
        if self._traversal.match_and_if_so_advance([TokenType.LEFT_BRACE]):
            return self._block()

        return self._expression_statement()

    def _block(self):
        statements = []
        while not self._traversal.match(TokenType.RIGHT_BRACE) and not self._traversal.at_end():
            statements.append(self._declaration())

        assert self._traversal.match_and_if_so_advance([TokenType.RIGHT_BRACE]), \
            "Expected closing '}'"

        return statement.BlockStmt(statements)

    def _expression_statement(self):
        expr = self._expression()
        stmt = statement.ExpressionStmt(expr)

        return stmt

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

        if self._traversal.match_and_if_so_advance([TokenType.IDENTIFIER]):
            return expression.VariableExpr(self._traversal.previous())

        if self._traversal.match_and_if_so_advance([TokenType.LEFT_PARENTHESIS]):
            expr = self._expression()
            assert self._traversal.match_and_if_so_advance([TokenType.RIGHT_PARENTHESIS]), \
                "Expected ')' after expression. At {}".format(
                    self._traversal.get())

            return expression.GroupingExpr(expr)

        raise Exception("Caused by {}".format(self._traversal.get()))
