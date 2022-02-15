from enum import auto, Enum


class Parenthesis:

    def __init__(self, inner_expr):
        self.inner_expr = inner_expr


class Literal:

    def __init__(self, literal_token):
        self.literal_token = literal_token


class Variable:

    class VariableType(Enum):
        MACRO = auto(),
        VARIABLE = auto()

    def __init__(self, identifier_token, variable_type):
        self.identifier_token = identifier_token
        self.variable_type = variable_type

    def is_macro(self):
        return self.variable_type == Variable.VariableType.MACRO


class SceneIdentifier:

    def __init__(self, identifier_token):
        self.identifier_token = identifier_token


class FunctionCall:

    def __init__(self, identifier_token, arguments):
        self.identifier_token = identifier_token
        self.arguments = arguments


class Unary:

    def __init__(self, operator_token, expr):
        self.operator_token = operator_token
        self.expr = expr


class Binary:

    def __init__(self, left_expr, operator_token, right_expr):
        self.left_expr = left_expr
        self.operator_token = operator_token
        self.right_expr = right_expr
