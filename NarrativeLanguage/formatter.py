from NarrativeLanguage import expression
from NarrativeLanguage.visitor import Visitor

FORMATTER = Visitor()


def _format_literal_expr(expr):
    return repr(expr.token.literal)


def _format_unary_expr(expr):
    return "{}{}".format(
        expr.operator.lexeme, FORMATTER.visit(expr.expression))


def _format_binary_expr(expr):
    return "{} {} {}".format(
        FORMATTER.visit(expr.left),
        expr.operator.lexeme,
        FORMATTER.visit(expr.right)
    )


def _format_grouping_expr(expr):
    return "({})".format(FORMATTER.visit(expr.expression))


FORMATTER.submit(expression.LiteralExpr, _format_literal_expr) \
    .submit(expression.UnaryExpr, _format_unary_expr) \
    .submit(expression.BinaryExpr, _format_binary_expr) \
    .submit(expression.GroupingExpr, _format_grouping_expr)
