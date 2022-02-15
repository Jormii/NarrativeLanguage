from NarrativeLanguage import expression, statement
from NarrativeLanguage.token import TokenType
from NarrativeLanguage.visitor import Visitor

from NarrativeLanguage.formatter import FORMATTER


class Environment:

    def __init__(self, parent=None):
        self._variables = {}
        self._parent = parent

    def _fetch_scope(self, name):
        if name in self._variables:
            return self
        elif self._parent is not None:
            return self._parent._fetch_scope(name)

        return None

    def read(self, name):
        scope = self._fetch_scope(name)
        assert scope is not None, "Undefined variable"

        return scope._variables[name]

    def write(self, name, value):
        scope = self._fetch_scope(name)
        if scope is None:
            scope = self

        scope._variables[name] = value


INTERPRETER = Visitor()
MACROS = Environment()
ENVIRONMENT = Environment()


# region Statements


# endregion

def _interpret_print_stmt(stmt):
    string = stmt.string_token.literal
    print(string)

    return string


def _interpret_expression_stmt(stmt):
    return INTERPRETER.visit(stmt.expr)


def _interpret_macro_declaration_stmt(stmt):
    return _write_variable(stmt.assignment_stmt, MACROS)


def _interpret_assignment_stmt(stmt):
    return _write_variable(stmt, ENVIRONMENT)


def _write_variable(assignment_stmt, environment):
    identifier = assignment_stmt.identifier_token.lexeme
    value = INTERPRETER.visit(assignment_stmt.assignment_expr)
    environment.write(identifier, value)

    return value


def _interpret_block_stmt(stmt):
    global ENVIRONMENT
    OLD_ENVIRONMENT = ENVIRONMENT
    ENVIRONMENT = Environment(OLD_ENVIRONMENT)

    stmts_returns = []
    for inner_stmt in stmt.statements:
        stmts_returns.append(INTERPRETER.visit(inner_stmt))

    ENVIRONMENT = OLD_ENVIRONMENT

    return stmts_returns


def _interpret_condition_stmt(stmt):
    if INTERPRETER.visit(stmt.if_condition):
        return INTERPRETER.visit(stmt.if_block)

    for i in range(len(stmt.elifs_blocks)):
        c = stmt.elifs_conditions[i]
        b = stmt.elifs_blocks[i]
        if INTERPRETER.visit(c):
            return INTERPRETER.visit(b)

    if stmt.else_block is not None:
        return INTERPRETER.visit(stmt.else_block)

    return None


def _interpret_option_stmt(stmt):
    option_string = stmt.string_token.literal
    print(FORMATTER.visit(stmt))

    return "OPTION: {}".format(option_string)


INTERPRETER.submit(statement.Print, _interpret_print_stmt) \
    .submit(statement.Expression, _interpret_expression_stmt) \
    .submit(statement.MacroDeclaration, _interpret_macro_declaration_stmt) \
    .submit(statement.Assignment, _interpret_assignment_stmt) \
    .submit(statement.Block, _interpret_block_stmt) \
    .submit(statement.Condition, _interpret_condition_stmt) \
    .submit(statement.Option, _interpret_option_stmt)

# region Expressions


def _interpret_parenthesis_expr(expr):
    return INTERPRETER.visit(expr.inner_expr)


def _interpret_literal_expr(expr):
    return expr.literal_token.literal


def _interpret_variable_expr(expr):
    identifier = expr.identifier_token.lexeme
    if expr.is_macro():
        return MACROS.read(identifier)
    else:
        return ENVIRONMENT.read(identifier)


def _interpret_scene_identifier_expr(expr):
    raise NotImplementedError()


def _interpret_function_call_expr(expr):
    return "CALL: {}".format(FORMATTER.visit(expr))


def _interpret_unary_expr(expr):
    op_token = expr.operator_token.type
    if op_token == TokenType.MINUS:
        return -INTERPRETER.visit(expr.expr)
    elif op_token == TokenType.BANG:
        return not INTERPRETER.visit(expr.expr)

    exit("Unknown unary operator {}".format(expr.token))


def _interpret_binary_expr(expr):
    left = INTERPRETER.visit(expr.left_expr)
    right = INTERPRETER.visit(expr.right_expr)

    op_token = expr.operator_token.type
    if op_token == TokenType.PLUS:
        return left + right
    elif op_token == TokenType.MINUS:
        return left - right
    elif op_token == TokenType.STAR:
        return left * right
    elif op_token == TokenType.SLASH:
        return left / right
    elif op_token == TokenType.EQUAL_EQUAL:
        return left == right
    elif op_token == TokenType.BANG_EQUAL:
        return left != right
    elif op_token == TokenType.LESS:
        return left < right
    elif op_token == TokenType.LESS_EQUAL:
        return left <= right
    elif op_token == TokenType.GREATER:
        return left > right
    elif op_token == TokenType.GREATER_EQUAL:
        return left >= right
    elif op_token == TokenType.AND:
        return left and right
    elif op_token == TokenType.OR:
        return left or right

    exit("Unknown binary operator {}".format(expr.token))


INTERPRETER.submit(expression.Parenthesis, _interpret_parenthesis_expr) \
    .submit(expression.Literal, _interpret_literal_expr) \
    .submit(expression.Variable, _interpret_variable_expr) \
    .submit(expression.SceneIdentifier, _interpret_scene_identifier_expr) \
    .submit(expression.FunctionCall, _interpret_function_call_expr) \
    .submit(expression.Unary, _interpret_unary_expr) \
    .submit(expression.Binary, _interpret_binary_expr)

# endregion
