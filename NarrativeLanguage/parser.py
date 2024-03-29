import traceback

from NarrativeLanguage import expression, statement, reporting
from NarrativeLanguage.token import Token, TokenType


class TokenTraversal:

    def __init__(self, tokens):
        self.tokens = tokens

        self._pos = 0

    def at_end(self):
        return self.tokens[self._pos].type == TokenType.EOF

    def match(self, token_types):
        if self.at_end():
            return False

        if not isinstance(token_types, list):
            token_types = [token_types]

        token = self.tokens[self._pos]
        for t in token_types:
            if token.type == t:
                return True

        return False

    def match_and_if_so_advance(self, token_types, write_to=None):
        match = self.match(token_types)
        if match:
            if write_to is not None:
                self._copy_to(write_to)
            self._pos += 1

        return match

    def _copy_to(self, dst):
        token = self.tokens[self._pos]
        dst.type = token.type
        dst.lexeme = token.lexeme
        dst.literal = token.literal
        dst.line = token.line
        dst.column = token.column

    def peek_match(self, token_types):
        self._pos += 1
        match = self.match(token_types)
        self._pos -= 1

        return match


class Parser:

    EQUALITY_TOKENS = [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]
    COMPARISON_TOKENS = [TokenType.LESS, TokenType.LESS_EQUAL,
                         TokenType.GREATER, TokenType.GREATER_EQUAL]
    TERM_TOKENS = [TokenType.PLUS, TokenType.MINUS]
    FACTOR_TOKENS = [TokenType.STAR, TokenType.SLASH]
    NEGATION_TOKENS = [TokenType.MINUS, TokenType.BANG]
    LITERAL_TOKENS = [TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING]

    def __init__(self, tokens):
        self.tokens = tokens
        self.statements = []

        self._tt = TokenTraversal(tokens)

    def parse(self):
        try:
            while not self._tt.at_end():
                pos = self._tt._pos
                stmt = self._statement()
                self.statements.append(stmt)
        except Exception as e:
            print(traceback.format_exc())

            token = self.tokens[pos]
            reporting.error(
                token.line, "Parsing statement starting at {}".format(token))
            print(e)
            exit()

    def _statement(self):
        if self._tt.match(TokenType.IDENTIFIER):
            return self._identifier_leading_statement()
        elif self._tt.match(TokenType.STRING):
            return self._string_leading_statement()
        elif self._tt.match(TokenType.LEFT_BRACE):
            return self._block()
        elif self._tt.match(TokenType.GLOBAL):
            return self._global_variable()
        elif self._tt.match(TokenType.STORE):
            return self._store_variable()
        elif self._tt.match(TokenType.IF):
            return self._condition()
        elif self._tt.match(TokenType.LEFT_SQR_BRACKET):
            return self._scene_switch()

        return self._expression_statement()

    def _identifier_leading_statement(self):
        if self._tt.peek_match(TokenType.EQUAL):
            return self._assignment()

        return self._expression_statement()

    def _assignment(self):
        # FORMAT
        # IDENTIFIER '=' EXPRESSION ';'

        identifier_token = Token.empty()
        assert self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, identifier_token), \
            "Expected identifier before assignment"
        assert self._tt.match_and_if_so_advance(TokenType.EQUAL), \
            "Expected '=' after identifier"

        assignment_expr = self._expression()

        assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
            "Expected ';' after assignment"

        return statement.Assignment(identifier_token, assignment_expr)

    def _string_leading_statement(self):
        if self._tt.peek_match(TokenType.EQUAL):
            return self._option_definition_statement()

        return self._print_statement()

    def _option_definition_statement(self):
        # FORMAT
        # STRING '=' BLOCK

        string_token = Token.empty()
        assert self._tt.match_and_if_so_advance(TokenType.STRING, string_token), \
            "Expected STRING literal"
        assert self._tt.match_and_if_so_advance(TokenType.EQUAL), \
            "Expected '='"

        block_stmt = self._block()

        return statement.Option(string_token, block_stmt)

    def _print_statement(self):
        # FORMAT
        # STRING ';'
        string_token = Token.empty()
        assert self._tt.match_and_if_so_advance(TokenType.STRING, string_token), \
            "Expected string literal"
        assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
            "Expected ';'"

        return statement.Print(string_token)

    def _block(self):
        # FORMAT
        # '{' (STATEMENT)* '}'

        assert self._tt.match_and_if_so_advance(TokenType.LEFT_BRACE), \
            "Expected '{'"

        statements = []
        while not self._tt.match(TokenType.RIGHT_BRACE):
            statements.append(self._statement())

        assert self._tt.match_and_if_so_advance(TokenType.RIGHT_BRACE), \
            "Expected '}'"

        return statement.Block(statements)

    def _global_variable(self):
        # FORMAT
        # GLOBAL ((IDENTIFIER ';') | ASSIGNMENT)

        assert self._tt.match_and_if_so_advance(TokenType.GLOBAL), \
            "Expected 'GLOBAL'"

        if self._tt.peek_match(TokenType.SEMICOLON):
            identifier_token = Token.empty()
            self._tt.match_and_if_so_advance(
                TokenType.IDENTIFIER, identifier_token)

            assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
                "Expected ';'"

            stmt = statement.GlobalDeclaration(identifier_token)
        else:
            stmt = statement.GlobalDefinition(self._assignment())

        return stmt

    def _store_variable(self):
        # FORMAT
        # STORE ASSIGNMENT

        assert self._tt.match_and_if_so_advance(TokenType.STORE), \
            "Expected 'STORE'"

        assignment_stmt = self._assignment()
        return statement.Store(assignment_stmt)

    def _condition(self):
        # FORMAT
        # 'IF' '(' EXPRESSION ')' BLOCK (ELIF '(' EXPRESSION ')' BLOCK)* (ELSE BLOCK)?

        # 'IF'
        assert self._tt.match_and_if_so_advance(TokenType.IF), \
            "Expected 'IF'"
        assert self._tt.match_and_if_so_advance(TokenType.LEFT_PARENTHESIS), \
            "Expected '('"

        if_condition = self._expression()
        assert self._tt.match_and_if_so_advance(TokenType.RIGHT_PARENTHESIS), \
            "Expected ')'"

        if_block = self._block()

        # 'ELIF'
        elifs_conditions = []
        elifs_blocks = []
        while self._tt.match_and_if_so_advance(TokenType.ELIF):
            assert self._tt.match_and_if_so_advance(TokenType.LEFT_PARENTHESIS), \
                "Expected '('"

            elifs_conditions.append(self._expression())

            assert self._tt.match_and_if_so_advance(TokenType.RIGHT_PARENTHESIS), \
                "Expected ')'"

            elifs_blocks.append(self._block())

        # 'ELSE'
        else_block = None
        if self._tt.match_and_if_so_advance(TokenType.ELSE):
            else_block = self._block()

        return statement.Condition(
            if_condition, if_block,
            elifs_conditions, elifs_blocks,
            else_block
        )

    def _scene_switch(self):
        # FORMAT
        # '[[' STRING ']]'

        for _ in range(2):
            assert self._tt.match_and_if_so_advance(TokenType.LEFT_SQR_BRACKET), \
                "Expected '[['"

        scene_identifier_token = Token.empty()
        assert self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, scene_identifier_token), \
            "Expected IDENTIFIER"

        for _ in range(2):
            assert self._tt.match_and_if_so_advance(TokenType.RIGHT_SQR_BRACKET), \
                "Expected ']]'"

        # Consume ";"
        assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
            "Expected ';'"

        return statement.SceneSwitch(scene_identifier_token)

    def _expression_statement(self):
        expr_stmt = statement.Expression(self._expression())
        assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
            "Expected ';'"

        return expr_stmt

    def _expression(self):
        return self._logical_or()

    def _logical_or(self):
        # FORMAT
        # AND ('OR' AND)*

        expr = self._logical_and()
        operator_token = Token.empty()
        while self._tt.match_and_if_so_advance(TokenType.OR, operator_token):
            right = self._logical_and()
            expr = expression.Binary(expr, operator_token, right)
            operator_token = Token.empty()

        return expr

    def _logical_and(self):
        # FORMAT
        # EQUALITY ('AND' EQUALITY)*

        expr = self._equality()
        operator_token = Token.empty()
        while self._tt.match_and_if_so_advance(TokenType.AND, operator_token):
            right = self._equality()
            expr = expression.Binary(expr, operator_token, right)
            operator_token = Token.empty()

        return expr

    def _equality(self):
        # FORMAT
        # COMPARISON (('==' | '!=') COMPARISON)*

        expr = self._comparison()
        operator_token = Token.empty()
        while self._tt.match_and_if_so_advance(Parser.EQUALITY_TOKENS, operator_token):
            right = self._comparison()
            expr = expression.Binary(expr, operator_token, right)
            operator_token = Token.empty()

        return expr

    def _comparison(self):
        # FORMAT
        # TERM (('<' | '<=' | '>' | '>=') TERM)*

        expr = self._term()
        operator_token = Token.empty()
        while self._tt.match_and_if_so_advance(Parser.COMPARISON_TOKENS, operator_token):
            right = self._term()
            expr = expression.Binary(expr, operator_token, right)
            operator_token = Token.empty()

        return expr

    def _term(self):
        # FORMAT
        # FACTOR (('+' | '-') FACTOR)*

        expr = self._factor()
        operator_token = Token.empty()
        while self._tt.match_and_if_so_advance(Parser.TERM_TOKENS, operator_token):
            right = self._factor()
            expr = expression.Binary(expr, operator_token, right)
            operator_token = Token.empty()

        return expr

    def _factor(self):
        # FORMAT
        # NEGATION (('*' | '/') NEGATION)*

        expr = self._negation()
        operator_token = Token.empty()
        while self._tt.match_and_if_so_advance(Parser.FACTOR_TOKENS, operator_token):
            right = self._negation()
            expr = expression.Binary(expr, operator_token, right)
            operator_token = Token.empty()

        return expr

    def _negation(self):
        # FORMAT
        # (('-' | '!') NEGATION) | (LITERAL_AND_PARENTHESIS)

        operator_token = Token.empty()
        if self._tt.match_and_if_so_advance(Parser.NEGATION_TOKENS, operator_token):
            expr = self._negation()
            return expression.Unary(operator_token, expr)

        return self._literal_and_parenthesis()

    def _literal_and_parenthesis(self):
        # FORMAT
        # ('(' EXPRESSION ')') | LITERAL | ('#' IDENTIFIER) | IDENTIFIER |
        #   (IDENTIFIER ARGUMENTS) | ('[[' IDENTIFIER ']]')

        # Grouping
        if self._tt.match_and_if_so_advance(TokenType.LEFT_PARENTHESIS):
            expr = expression.Parenthesis(self._expression())
            assert self._tt.match_and_if_so_advance(TokenType.RIGHT_PARENTHESIS), \
                "Expected ')'"

            return expr

        # Literal
        literal_token = Token.empty()
        if self._tt.match_and_if_so_advance(Parser.LITERAL_TOKENS, literal_token):
            return expression.Literal(literal_token)

        # Identifier or function call
        identifier_token = Token.empty()
        if self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, identifier_token):
            if self._tt.match(TokenType.LEFT_PARENTHESIS):
                arguments = self._arguments()
                return expression.FunctionCall(identifier_token, arguments)

            return expression.Variable(identifier_token)

        # Notify error
        raise Exception("Cannot parse expression")

    def _arguments(self):
        # FORMAT
        # '(' EXPRESSION (',' EXPRESSION)* ')'

        assert self._tt.match_and_if_so_advance(TokenType.LEFT_PARENTHESIS), \
            "Expected '('"

        arguments = []
        while not self._tt.match(TokenType.RIGHT_PARENTHESIS):
            arguments.append(self._expression())

            if not self._tt.match(TokenType.RIGHT_PARENTHESIS):
                assert self._tt.match_and_if_so_advance(TokenType.COMMA), \
                    "Expected ','"

        assert self._tt.match_and_if_so_advance(TokenType.RIGHT_PARENTHESIS), \
            "Expected ')'"

        return arguments
