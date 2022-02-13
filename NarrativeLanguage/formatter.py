from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor

FORMATTER = Visitor()
DEPTH = 0


def _tabs():
    return 4 * ' ' * DEPTH

# region Statements


def _format_expression_stmt(stmt):
    return "{}{}".format(_tabs(), FORMATTER.visit(stmt.expr))


def _format_variable_stmt(stmt):
    formatted = "{}{} {}".format(
        _tabs(), stmt.type_token.lexeme, stmt.identifier_token.lexeme)
    if stmt.initializer_expr is not None:
        formatted = "{} = {}".format(
            formatted, FORMATTER.visit(stmt.initializer_expr))

    return formatted


def _format_block_stmt(stmt):
    global DEPTH

    formatted = "{}{{\n".format(_tabs())
    DEPTH += 1

    for sub_stmt in stmt.statements:
        formatted = "{}{}\n".format(formatted, FORMATTER.visit(sub_stmt))

    DEPTH -= 1
    formatted = "{}{}}}".format(formatted, _tabs())

    return formatted


FORMATTER.submit(statement.ExpressionStmt, _format_expression_stmt) \
    .submit(statement.VariableStmt, _format_variable_stmt) \
    .submit(statement.BlockStmt, _format_block_stmt)

# endregion

# region Expressions


def _format_literal_expr(expr):
    return repr(expr.token.literal)


def _format_variable_expr(expr):
    return "${}".format(expr.identifier_token.lexeme)


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
    .submit(expression.VariableExpr, _format_variable_expr) \
    .submit(expression.UnaryExpr, _format_unary_expr) \
    .submit(expression.BinaryExpr, _format_binary_expr) \
    .submit(expression.GroupingExpr, _format_grouping_expr)

# endregion
