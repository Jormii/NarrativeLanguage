class IStatement:

    pass


class ExpressionStmt(IStatement):

    def __init__(self, expr):
        self.expr = expr


class VariableStmt(IStatement):

    def __init__(self, type_token, identifier_token, initializer_expr):
        self.type_token = type_token
        self.identifier_token = identifier_token
        self.initializer_expr = initializer_expr


class BlockStmt(IStatement):

    def __init__(self, statements):
        self.statements = statements
