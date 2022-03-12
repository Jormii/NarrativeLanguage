from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor

FORMATTER = Visitor()
DEPTH = 0


def _tabs():
    return 4 * ' ' * DEPTH

# region Statements


def _format_print_stmt(stmt):
    return "{}PRINT: {};".format(_tabs(), stmt.string_token.lexeme)


def _format_expression_stmt(stmt):
    return "{}{};".format(_tabs(), FORMATTER.visit(stmt.expr))


def _format_global_declaration_stmt(stmt):
    return "{}GLOBAL {};".format(_tabs(), stmt.identifier_token.lexeme)


def _format_global_definition_stmt(stmt):
    assignment_str = FORMATTER.visit(stmt.assignment_stmt)
    return "{}GLOBAL {}".format(_tabs(), assignment_str)


def _format_store_declaration_stmt(stmt):
    assignment_str = FORMATTER.visit(stmt.assignment_stmt)
    return "{}STORE {}".format(_tabs(), assignment_str)


def _format_assignment_stmt(stmt):
    return "{}${} = {};".format(
        _tabs(), stmt.identifier_token.lexeme, FORMATTER.visit(stmt.assignment_expr))


def _format_block_stmt(stmt):
    global DEPTH

    formatted = "{}{{\n".format(_tabs())
    DEPTH += 1

    for inner_stmt in stmt.statements:
        formatted = "{}{}\n".format(formatted, FORMATTER.visit(inner_stmt))

    DEPTH -= 1
    formatted = "{}{}}}".format(formatted, _tabs())

    return formatted


def _format_condition_stmt(stmt):
    formatted = "{}IF ({}) {}".format(
        _tabs(),
        FORMATTER.visit(stmt.if_condition),
        FORMATTER.visit(stmt.if_block)
    )

    for i in range(len(stmt.elifs_blocks)):
        c = stmt.elifs_conditions[i]
        b = stmt.elifs_blocks[i]
        formatted = "{} ELIF ({}) {}".format(
            formatted, FORMATTER.visit(c), FORMATTER.visit(b))

    if stmt.else_block is not None:
        formatted = "{} ELSE {}".format(
            formatted, FORMATTER.visit(stmt.else_block))

    return formatted


def _format_option_stmt(stmt):
    return "{}{} = {}".format(
        _tabs(), stmt.string_token.lexeme,
        FORMATTER.visit(stmt.block_stmt))


FORMATTER.submit(statement.Print, _format_print_stmt) \
    .submit(statement.Expression, _format_expression_stmt) \
    .submit(statement.GlobalDeclaration, _format_global_declaration_stmt) \
    .submit(statement.GlobalDefinition, _format_global_definition_stmt) \
    .submit(statement.Store, _format_store_declaration_stmt) \
    .submit(statement.Assignment, _format_assignment_stmt) \
    .submit(statement.Block, _format_block_stmt) \
    .submit(statement.Condition, _format_condition_stmt) \
    .submit(statement.Option, _format_option_stmt)

# endregion

# region Expressions


def _format_parenthesis_expr(expr):
    return "({})".format(FORMATTER.visit(expr.inner_expr))


def _format_literal_expr(expr):
    return "({}) {}".format(
        expr.literal_token.type.name,
        expr.literal_token.lexeme
    )


def _format_variable_expr(expr):
    return "{}{}".format("$", expr.identifier_token.lexeme)


def _format_scene_identifier_expr(expr):
    return "[[{}]]".format(expr.identifier_token.lexeme)


def _format_function_call_expr(expr):
    formatted_args = []
    for arg in expr.arguments:
        formatted_args.append(FORMATTER.visit(arg))

    return "{}({})".format(
        expr.identifier_token.lexeme, ", ".join(formatted_args))


def _format_unary_expr(expr):
    return "{}{}".format(
        expr.operator_token.lexeme,
        FORMATTER.visit(expr.expr)
    )


def _format_binary_expr(expr):
    return "{} {} {}".format(
        FORMATTER.visit(expr.left_expr),
        expr.operator_token.lexeme,
        FORMATTER.visit(expr.right_expr)
    )


FORMATTER.submit(expression.Parenthesis, _format_parenthesis_expr) \
    .submit(expression.Literal, _format_literal_expr) \
    .submit(expression.Variable, _format_variable_expr) \
    .submit(expression.SceneIdentifier, _format_scene_identifier_expr) \
    .submit(expression.FunctionCall, _format_function_call_expr) \
    .submit(expression.Unary, _format_unary_expr) \
    .submit(expression.Binary, _format_binary_expr)

# endregion
