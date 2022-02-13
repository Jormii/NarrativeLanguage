class IExpression:

    pass


class LiteralExpr(IExpression):

    def __init__(self, token):
        self.token = token


class VariableExpr(IExpression):

    def __init__(self, identifier_token):
        self.identifier_token = identifier_token


class UnaryExpr(IExpression):

    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression


class BinaryExpr(IExpression):

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class GroupingExpr(IExpression):

    def __init__(self, expression):
        self.expression = expression
