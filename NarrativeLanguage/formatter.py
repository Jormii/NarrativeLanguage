from NarrativeLanguage import expression


def format_expression(expr):
    t = type(expr)
    cb = PRINT_EXPRESSION_CB.get(t)
    assert cb is not None, \
        "Can't print expression of type {}".format(t)

    return cb(expr)


def _format_literal_expr(expr):
    return repr(expr.token.literal)


def _format_unary_expr(expr):
    return "{}{}".format(
        expr.operator.lexeme, format_expression(expr.expression))


def _format_binary_expr(expr):
    return "{} {} {}".format(
        format_expression(expr.left),
        expr.operator.lexeme,
        format_expression(expr.right)
    )


def _format_grouping_expr(expr):
    return "({})".format(format_expression(expr.expression))


PRINT_EXPRESSION_CB = {
    expression.LiteralExpr: _format_literal_expr,
    expression.UnaryExpr: _format_unary_expr,
    expression.BinaryExpr: _format_binary_expr,
    expression.GroupingExpr: _format_grouping_expr
}
