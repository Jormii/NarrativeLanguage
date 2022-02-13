from NarrativeLanguage import expression, statement
from NarrativeLanguage.token import TokenType
from NarrativeLanguage.visitor import Visitor


class Environment:

    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def exists(self, name):
        if name in self.variables:
            return True
        elif self.parent is not None:
            return self.parent.exists(name)

        return False

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            exit("Unknown variable \"{}\"".format(name))

    def create(self, name, value):
        assert not self.exists(name), \
            "Variable \"{}\" already defined".format(name)

        self.variables[name] = value

    def update(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent is not None:
            self.parent.update(name, value)
        else:
            exit("Undefined variable \"{}\"".format(name))


INTERPRETER = Visitor()
ENVIRONMENT = Environment()


# region Statements


def _interpret_expression_stmt(stmt):
    return INTERPRETER.visit(stmt.expr)


def _interpret_variable_stmt(stmt):
    t = stmt.type_token.type
    if t == TokenType.STRING:
        value = ""
    elif t == TokenType.INT_KEYWORD:
        value = 0
    elif t == TokenType.FLOAT_KEYWORD:
        value = 0.0
    else:
        exit("Unknown variable type {}".format(t))

    initializer = stmt.initializer_expr
    if initializer is not None:
        value = INTERPRETER.visit(initializer)

    name = stmt.identifier_token.lexeme
    ENVIRONMENT.create(name, value)

    return value


def _interpret_block_stmt(stmt):
    global ENVIRONMENT
    OLD_ENVIRONMENT = ENVIRONMENT
    ENVIRONMENT = Environment(OLD_ENVIRONMENT)

    results = []
    for sub_stmt in stmt.statements:
        r = INTERPRETER.visit(sub_stmt)
        results.append(r)

    ENVIRONMENT = OLD_ENVIRONMENT

    return results


INTERPRETER.submit(statement.ExpressionStmt, _interpret_expression_stmt) \
    .submit(statement.VariableStmt, _interpret_variable_stmt) \
    .submit(statement.BlockStmt, _interpret_block_stmt)

# endregion

# region Expressions


def _interpret_literal_expr(expr):
    return expr.token.literal   # TODO: Macros


def _interpret_variable_expr(expr):
    name = expr.identifier_token.lexeme
    return ENVIRONMENT.get(name)


def _interpret_unary_expr(expr):
    if expr.operator.token_type == TokenType.MINUS:
        return -INTERPRETER.visit(expr.expression)
    elif expr.operator.token_type == TokenType.BANG:
        return not INTERPRETER.visit(expr.expression)

    exit("Unknown unary operator {}".format(expr.operator))


def _interpret_binary_expr(expr):
    left = INTERPRETER.visit(expr.left)
    right = INTERPRETER.visit(expr.right)

    op_token = expr.operator.type
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

    exit("Unknown binary operator {}".format(expr.operator))


def _interpret_grouping_expr(expr):
    return INTERPRETER.visit(expr.expression)


INTERPRETER.submit(expression.LiteralExpr, _interpret_literal_expr) \
    .submit(expression.VariableExpr, _interpret_variable_expr) \
    .submit(expression.UnaryExpr, _interpret_unary_expr) \
    .submit(expression.BinaryExpr, _interpret_binary_expr) \
    .submit(expression.GroupingExpr, _interpret_grouping_expr)

# endregion
