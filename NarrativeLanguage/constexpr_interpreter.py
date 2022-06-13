import NarrativeLanguage.expression as expression
import NarrativeLanguage.variables as variables
from NarrativeLanguage.token import TokenType
from NarrativeLanguage.visitor import Visitor


class ConstExprInterpreter(Visitor):

    def __init__(self):
        super().__init__()

        self.solver = None


class NotConstExprException(Exception):

    def __init__(self, msg):
        super().__init__()

        self.msg = msg


CONSTEXPR_INTERPRETER = ConstExprInterpreter()


class Operator:

    def calculate(self):
        raise NotImplementedError


class UnaryOperator(Operator):

    def __init__(self):
        self.value = 0


class BinaryOperator(Operator):

    def __init__(self):
        self.left_value = 0
        self.right_value = 0

# region Operators classes


class UnaryNegate(UnaryOperator):

    def calculate(self):
        return variables.Value(self.value.value_type, -self.value.literal)


class UnaryNot(UnaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(not bool(self.value.literal))
        )


class BinaryAdd(BinaryOperator):

    def calculate(self):
        return variables.Value(
            self.left_value.value_type,
            self.left_value.literal + self.right_value.literal
        )


class BinarySubstract(BinaryOperator):

    def calculate(self):
        return variables.Value(
            self.left_value.value_type,
            self.left_value.literal - self.right_value.literal
        )


class BinaryMultiply(BinaryOperator):

    def calculate(self):
        return variables.Value(
            self.left_value.value_type,
            self.left_value.literal * self.right_value.literal
        )


class BinaryDivide(BinaryOperator):

    def calculate(self):
        return variables.Value(
            self.left_value.value_type,
            self.left_value.literal / self.right_value.literal
        )


class BinaryEqual(BinaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(self.left_value.literal == self.right_value.literal)
        )


class BinaryNotEqual(BinaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(self.left_value.literal != self.right_value.literal)
        )


class BinaryLessThan(BinaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(self.left_value.literal < self.right_value.literal)
        )


class BinaryLessOrEqual(BinaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(self.left_value.literal <= self.right_value.literal)
        )


class BinaryGreaterThan(BinaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(self.left_value.literal > self.right_value.literal)
        )


class BinaryGreaterOrEqual(BinaryOperator):

    def calculate(self):
        return variables.Value(
            variables.VALUE_TYPES[variables.ValueType.Class.INT],
            int(self.left_value.literal >= self.right_value.literal)
        )


UNARY_OPERATOR_MAPPING = {
    TokenType.MINUS: UnaryNegate(),
    TokenType.BANG: UnaryNot()
}

BINARY_OPERATOR_MAPPING = {
    TokenType.PLUS: BinaryAdd(),
    TokenType.MINUS: BinarySubstract(),
    TokenType.STAR: BinaryMultiply(),
    TokenType.SLASH: BinaryDivide(),
    TokenType.EQUAL_EQUAL: BinaryEqual(),
    TokenType.BANG_EQUAL: BinaryNotEqual(),
    TokenType.LESS: BinaryLessThan(),
    TokenType.LESS_EQUAL: BinaryLessOrEqual(),
    TokenType.GREATER: BinaryGreaterThan(),
    TokenType.GREATER_EQUAL: BinaryGreaterOrEqual()
}

# end region


def _constexpr_parenthesis(expr):
    return CONSTEXPR_INTERPRETER.visit(expr.inner_expr)


def _constexpr_literal(expr):
    from NarrativeLanguage.variable_solver import value_from_token
    return value_from_token(expr.literal_token)


def _constexpr_variable(expr):
    exit("Reading variables is not constexpr")


def _constexpr_function_call(expr):
    raise NotConstExprException("Function calls are not constexpr")


def _constexpr_unary(expr):
    value = CONSTEXPR_INTERPRETER.visit(expr.expr)
    return calculate_unary_expr(expr.operator_token, value)


def _constexpr_binary(expr):
    left_value = CONSTEXPR_INTERPRETER.visit(expr.left_expr)
    right_value = CONSTEXPR_INTERPRETER.visit(expr.right_expr)
    return calculate_binary_expr(expr.operator_token, left_value, right_value)


CONSTEXPR_INTERPRETER.submit(expression.Parenthesis, _constexpr_parenthesis) \
    .submit(expression.Literal, _constexpr_literal) \
    .submit(expression.Variable, _constexpr_variable) \
    .submit(expression.FunctionCall, _constexpr_function_call) \
    .submit(expression.Unary, _constexpr_unary) \
    .submit(expression.Binary, _constexpr_binary)


def calculate_unary_expr(op_token, value):
    assert _is_int_or_float(value), \
        "Operations can only be performed on ints or floats"

    op = UNARY_OPERATOR_MAPPING[op_token.type]
    op.value = value
    return op.calculate()


def calculate_binary_expr(op_token, left_value, right_value):
    assert left_value.value_type == right_value.value_type, \
        "Values must be of the same type"

    assert _is_int_or_float(left_value), \
        "Operations can only be performed on ints or floats"

    op = BINARY_OPERATOR_MAPPING[op_token.type]
    op.left_value = left_value
    op.right_value = right_value
    return op.calculate()


def _is_int_or_float(value):
    return value.value_type in [variables.INT_TYPE, variables.FLOAT_TYPE]
