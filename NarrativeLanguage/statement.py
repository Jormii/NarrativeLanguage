class Print:

    def __init__(self, string_token):
        self.string_token = string_token


class Expression:

    def __init__(self, expr):
        self.expr = expr


class MacroDeclaration:

    def __init__(self, assignment_stmt):
        self.assignment_stmt = assignment_stmt


class VariableDeclaration:

    def __init__(self, identifier_token, initializer_expr):
        self.identifier_token = identifier_token
        self.initializer_expr = initializer_expr


class Assigment:

    def __init__(self, identifier_token, assignment_expr):
        self.identifier_token = identifier_token
        self.assigment_expr = assignment_expr


class Block:

    def __init__(self, statements):
        self.statements = statements


class Condition:

    def __init__(self, if_condition, if_block, elifs_conditions, elifs_blocks, else_block):
        self.if_condition = if_condition
        self.if_block = if_block
        self.elifs_conditions = elifs_conditions
        self.elifs_blocks = elifs_blocks
        self.else_block = else_block


class Option:

    def __init__(self, string_token, block_stmt):
        self.string_token = string_token
        self.block_stmt = block_stmt
