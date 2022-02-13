from NarrativeLanguage import expression
from NarrativeLanguage.token import TokenType
from NarrativeLanguage.visitor import Visitor

INTERPRETER = Visitor()


def _interpret_literal_expr(expr):
    return expr.token.literal   # TODO: Macros


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
    .submit(expression.UnaryExpr, _interpret_unary_expr) \
    .submit(expression.BinaryExpr, _interpret_binary_expr) \
    .submit(expression.GroupingExpr, _interpret_grouping_expr)
