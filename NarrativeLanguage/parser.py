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

    TYPE_TOKENS = [TokenType.INT_KEYWORD,
                   TokenType.FLOAT_KEYWORD, TokenType.STRING_KEYWORD]

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
        if self._tt.match(TokenType.POUND):
            return self._macro_declaration()
        elif self._tt.match(Parser.TYPE_TOKENS):
            return self._variable_declaration()
        elif self._tt.match(TokenType.IDENTIFIER):
            return self._identifier_leading_statement()
        elif self._tt.match(TokenType.STRING):
            return self._string_leading_statement()
        elif self._tt.match(TokenType.LEFT_BRACE):
            return self._block()
        elif self._tt.match(TokenType.IF):
            return self._condition()

        return self._expression_statement()

    def _macro_declaration(self):
        # FORMAT
        # '#' VARIABLE DECLARATION

        assert self._tt.match_and_if_so_advance(TokenType.POUND), \
            "Expected '#' before macro"

        if self._tt.match(TokenType.IDENTIFIER) and not self._tt.match(TokenType.EQUAL):
            # It's an expression
            self._tt._pos -= 1  # Undo advance caused by previous asser
            return self._expression_statement()

        declaration_stmt = self._variable_declaration()
        return statement.MacroDeclaration(declaration_stmt)

    def _variable_declaration(self):
        # FORMAT
        # ('INT' | 'FLOAT' | 'STR') IDENTIFIER '=' EXPRESSION ';'
        type_token = Token.empty()
        identifier_token = Token.empty()

        assert self._tt.match_and_if_so_advance(Parser.TYPE_TOKENS, type_token), \
            "(INT | FLOAT | STR) expected before declaration"
        assert self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, identifier_token), \
            "Expected variable identifier"
        assert self._tt.match_and_if_so_advance(TokenType.EQUAL), \
            "Expected '=' after identifier"

        initializer_expr = self._expression()

        assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
            "Expected ';' after declaration"

        return statement.VariableDeclaration(
            type_token, identifier_token, initializer_expr)

    def _identifier_leading_statement(self):
        if self._tt.peek_match(TokenType.EQUAL):
            return self._assigment()

        return self._expression_statement()

    def _assigment(self):
        # FORMAT
        # IDENTIFIER '=' EXPRESSION;

        identifier_token = Token.empty()
        assert self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, identifier_token), \
            "Expected identifier before assignment"
        assert self._tt.match_and_if_so_advance(TokenType.EQUAL), \
            "Expected '=' after identifier"

        assignment_expr = self._expression()

        assert self._tt.match_and_if_so_advance(TokenType.SEMICOLON), \
            "Expected ';' after assignment"

        return statement.Assigment(identifier_token, assignment_expr)

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
        #   (IDENTIFIER ARGUMENTS)

        if self._tt.match_and_if_so_advance(TokenType.LEFT_PARENTHESIS):
            expr = expression.Parenthesis(self._expression())
            assert self._tt.match_and_if_so_advance(TokenType.RIGHT_PARENTHESIS), \
                "Expected ')'"

            return expr

        literal_token = Token.empty()
        if self._tt.match_and_if_so_advance(Parser.LITERAL_TOKENS, literal_token):
            return expression.Literal(literal_token)

        # Check if macro
        if self._tt.match_and_if_so_advance(TokenType.POUND):
            identifier_token = Token.empty()
            assert self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, identifier_token), \
                "Expected identifier after macro expression"

            return expression.Variable(
                identifier_token,
                expression.Variable.VariableType.MACRO
            )

        # Check if identifier or function call
        identifier_token = Token.empty()
        if self._tt.match_and_if_so_advance(TokenType.IDENTIFIER, identifier_token):
            if self._tt.match(TokenType.LEFT_PARENTHESIS):
                arguments = self._arguments()
                return expression.FunctionCall(identifier_token, arguments)

            return expression.Variable(
                identifier_token,
                expression.Variable.VariableType.VARIABLE
            )

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
