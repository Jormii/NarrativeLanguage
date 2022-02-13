from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor

FORMATTER = Visitor()

# region Statements


def _format_expression_stmt(stmt):
    return FORMATTER.visit(stmt.expr)


FORMATTER.submit(statement.ExpressionStmt, _format_expression_stmt)

# endregion

# region Expressions


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

# endregion
