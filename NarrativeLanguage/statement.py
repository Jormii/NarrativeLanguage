class Print:

    def __init__(self, string_token):
        self.string_token = string_token


class Expression:

    def __init__(self, expr):
        self.expr = expr


class GlobalDeclaration:

    def __init__(self, identifier_token):
        self.identifier_token = identifier_token


class GlobalDefinition:

    def __init__(self, assignment_stmt):
        self.assignment_stmt = assignment_stmt


class Store:

    def __init__(self, assignment_stmt):
        self.assignment_stmt = assignment_stmt


class Assignment:

    def __init__(self, identifier_token, assignment_expr):
        self.identifier_token = identifier_token
        self.assignment_expr = assignment_expr


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


class OptionVisibility:

    def __init__(self, action_token, string_token):
        self.action_token = action_token
        self.string_token = string_token
