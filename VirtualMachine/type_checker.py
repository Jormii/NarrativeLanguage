import VirtualMachine.variables as variables
from VirtualMachine.function import FunctionPrototypes

from NarrativeLanguage.token import TokenType
from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor


class TypeChecker:

    def __init__(self, statements, function_prototypes: FunctionPrototypes):
        self.statements = statements
        self.function_prototypes = function_prototypes

        self.macros = variables.Variables()
        self.defined_variable_identifiers = {}
        self.variables = {
            variables.VariableType.INT: variables.Variables(),
            variables.VariableType.FLOAT: variables.Variables(),
            variables.VariableType.STRING: variables.Variables()
        }

        self._checker = Visitor()
        self._checker.submit(statement.Print, self._check_print_stmt) \
            .submit(statement.Expression, self._check_expression_stmt) \
            .submit(statement.MacroDeclaration, self._check_macro_declaration_stmt) \
            .submit(statement.Assignment, self._check_assignment_stmt) \
            .submit(statement.Block, self._check_block_stmt) \
            .submit(statement.Condition, self._check_condition_stmt) \
            .submit(statement.Option, self._check_option_stmt)
        self._checker.submit(expression.Parenthesis, self._check_parenthesis_expr) \
            .submit(expression.Literal, self._check_literal_expr) \
            .submit(expression.Variable, self._check_variable_expr) \
            .submit(expression.SceneIdentifier, self._check_scene_identifier_expr) \
            .submit(expression.FunctionCall, self._check_function_call_expr) \
            .submit(expression.Unary, self._check_unary_expr) \
            .submit(expression.Binary, self._check_binary_expr)

        self._macro_solver = Visitor()
        self._macro_solver.submit(expression.Parenthesis, self._macro_solve_parenthesis_expr) \
            .submit(expression.Literal, self._macro_solve_literal_expr) \
            .submit(expression.Variable, self._macro_solve_variable_expr) \
            .submit(expression.SceneIdentifier, self._macro_solve_scene_identifier_expr) \
            .submit(expression.FunctionCall, self._macro_solve_function_call_expr) \
            .submit(expression.Unary, self._macro_solve_unary_expr) \
            .submit(expression.Binary, self._macro_solve_binary_expr)

    def check(self):
        for stmt in self.statements:
            self._checker.visit(stmt)

    def replace_macros_in_string(self, value):
        while True:
            pound_index = value.literal.find("#")
            if pound_index == -1:
                break

            end_index = pound_index + 1
            while end_index < len(value.literal):
                c = value.literal[end_index]
                if c.isalpha() or c.isdigit() or c == "_":
                    end_index += 1
                else:
                    break

            name = value.literal[pound_index+1:end_index]
            identifier = variables.Identifier(name)
            assert self.macro_is_defined(identifier), \
                "Unknown macro {}".format(identifier)

            variable = self.read_macro(identifier)
            replace_with = str(variable.value.literal)
            value.literal = value.literal[:pound_index] + \
                replace_with + value.literal[end_index:]

    def macro_is_defined(self, identifier):
        return self.macros.defined(identifier)

    def define_macro(self, identifier, value):
        if value.variable_type == variables.VariableType.STRING:
            self.replace_macros_in_string(value)

        # Create copies
        identifier = identifier.copy()
        value = value.copy()

        self.macros.define(identifier, value)

    def read_macro(self, identifier):
        return self.macros.read(identifier)

    def variable_is_defined(self, identifier):
        return identifier in self.defined_variable_identifiers

    def define_variable(self, identifier, value):
        if value.variable_type == variables.VariableType.STRING:
            self.replace_macros_in_string(value)

        # Create copies
        identifier = identifier.copy()
        value = value.copy()

        self.defined_variable_identifiers[identifier] = value.variable_type
        self.variables[value.variable_type].define(identifier, value)

    def read_variable(self, identifier):
        variable_type = self.defined_variable_identifiers[identifier]
        return self.variables[variable_type].read(identifier)

    def anonymous_variable_is_defined(self, value):
        identifier = anonymous_identifier(value)
        return self.variable_is_defined(identifier)

    def define_anonymous_variable(self, value):
        identifier = anonymous_identifier(value)
        self.define_variable(identifier, value)


# region Statements

    def _check_print_stmt(self, stmt):
        value = value_from_token(stmt.string_token)
        if not self.anonymous_variable_is_defined(value):
            self.define_anonymous_variable(value)

    def _check_expression_stmt(self, stmt):
        self._checker.visit(stmt.expr)

    def _check_macro_declaration_stmt(self, stmt):
        assignment_stmt = stmt.assignment_stmt
        identifier = identifier_from_token(assignment_stmt.identifier_token)
        value = self._macro_solver.visit(assignment_stmt.assignment_expr)

        assert not self.macro_is_defined(identifier), \
            "Macro {} is already defined".format(identifier)

        self.define_macro(identifier, value)

    def _check_assignment_stmt(self, stmt):
        identifier = identifier_from_token(stmt.identifier_token)
        value = self._checker.visit(stmt.assignment_expr)

        if self.variable_is_defined(identifier):
            variable = self.read_variable(identifier)
            assert variables.Value.congruent(value, variable.value)
        else:
            self.define_variable(identifier, value)

    def _check_block_stmt(self, stmt):
        for inner_stmt in stmt.statements:
            self._checker.visit(inner_stmt)

    def _check_condition_stmt(self, stmt):
        self._checker.visit(stmt.if_condition)
        self._checker.visit(stmt.if_block)

        for condition, block in zip(stmt.elifs_conditions, stmt.elifs_blocks):
            self._checker.visit(condition)
            self._checker.visit(block)

        if stmt.else_block is not None:
            self._checker.visit(stmt.else_block)

    def _check_option_stmt(self, stmt):
        value = value_from_token(stmt.string_token)
        if not self.anonymous_variable_is_defined(value):
            self.define_anonymous_variable(value)

        self._checker.visit(stmt.block_stmt)

    # endregion

    # region Expressions

    def _check_parenthesis_expr(self, expr):
        return self._checker.visit(expr.inner_expr)

    def _check_literal_expr(self, expr):
        return value_from_token(expr.literal_token)

    def _check_variable_expr(self, expr):
        identifier = identifier_from_token(expr.identifier_token)
        if expr.variable_type == expression.Variable.VariableType.MACRO:
            f_check = self.macro_is_defined
            f_read = self.read_macro
        else:
            f_check = self.variable_is_defined
            f_read = self.read_variable

        assert f_check(identifier), \
            "Variable {} isn't defined".format(identifier)

        variable = f_read(identifier)
        return variable.value

    def _check_scene_identifier_expr(self, expr):
        raise NotImplementedError()

    def _check_function_call_expr(self, expr):
        identifier = identifier_from_token(expr.identifier_token)
        arguments = []
        for arg_expr in expr.arguments:
            arguments.append(self._checker.visit(arg_expr))

        assert self.function_prototypes.defined(identifier), \
            "Unknown function {}".format(identifier)

        prototype = self.function_prototypes.get(identifier)
        assert len(prototype.params_types) == len(arguments), \
            "Mismatch in number of parameters and arguments"

        for param_type, arg in zip(prototype.params_types, arguments):
            dummy_value = variables.Value(param_type, 0)
            assert variables.Value.congruent(dummy_value, arg), \
                "Argument is not congruent with function param"

        # Functions always return an integer
        return variables.Value(variables.VariableType.INT, 0)

    def _check_unary_expr(self, expr):
        return self._checker.visit(expr.expr)

    def _check_binary_expr(self, expr):
        left_value = self._checker.visit(expr.left_expr)
        right_value = self._checker.visit(expr.right_expr)
        assert variables.Value.congruent(left_value, right_value), \
            "Values {} and {} aren't congruent".format(left_value, right_value)

        # TODO: Return value is weird
        return left_value

    # endregion

    # region Macro solver

    def _macro_solve_parenthesis_expr(self, expr):
        return self._macro_solver.visit(expr.inner_expr)

    def _macro_solve_literal_expr(self, expr):
        return value_from_token(expr.literal_token)

    def _macro_solve_variable_expr(self, expr):
        assert expr.variable_type == expression.Variable.VariableType.MACRO, \
            "Expected macro identifier"

        identifier = identifier_from_token(expr.identifier_token)
        assert self.macro_is_defined(identifier), \
            "Unknown macro {}".format(identifier)

        variable = self.read_macro(identifier)
        return variable.value

    def _macro_solve_scene_identifier_expr(self, expr):
        raise NotImplementedError()

    def _macro_solve_function_call_expr(self, expr):
        exit("Function can't be called from macro")

    def _macro_solve_unary_expr(self, expr):
        value = self._macro_solver.visit(expr.expr)
        assert value.variable_type != variables.VariableType.STRING, \
            "Can't perform operations on strings"

        op_token = expr.operator_token.type
        if op_token == TokenType.MINUS:
            variable_type = value.variable_type
            literal = -value.literal
        elif op_token == TokenType.BANG:
            variable_type = variables.VariableType.INT
            literal = int(not bool(value.literal))
        else:
            exit("Unknown unary token: {}".format(expr.operator_token))

        return variables.Value(variable_type, literal)

    def _macro_solve_binary_expr(self, expr):
        left = self._macro_solver.visit(expr.left_expr)
        right = self._macro_solver.visit(expr.right_expr)
        assert variables.Value.congruent(left, right), \
            "{} and {} aren't congruent".format(left, right)

        assert left.variable_type != variables.VariableType.STRING, \
            "Can't perform operations on strings"

        op_token = expr.operator_token.type
        if op_token == TokenType.PLUS:
            variable_type = left.variable_type
            literal = left.literal + right.literal
        elif op_token == TokenType.MINUS:
            variable_type = left.variable_type
            literal = left.literal - right.literal
        elif op_token == TokenType.STAR:
            variable_type = left.variable_type
            literal = left.literal * right.literal
        elif op_token == TokenType.SLASH:
            variable_type = left.variable_type
            literal = left.literal / right.literal
        elif op_token == TokenType.EQUAL_EQUAL:
            variable_type = variables.VariableType.INT
            literal = int(left.literal == right.literal)
        elif op_token == TokenType.BANG_EQUAL:
            variable_type = variables.VariableType.INT
            literal = int(left.literal != right.literal)
        elif op_token == TokenType.LESS:
            variable_type = variables.VariableType.INT
            literal = int(left.literal < right.literal)
        elif op_token == TokenType.LESS_EQUAL:
            variable_type = variables.VariableType.INT
            literal = int(left.literal <= right.literal)
        elif op_token == TokenType.GREATER:
            variable_type = variables.VariableType.INT
            literal = int(left.literal > right.literal)
        elif op_token == TokenType.GREATER_EQUAL:
            variable_type = variables.VariableType.INT
            literal = int(left.literal >= right.literal)
        elif op_token == TokenType.AND:
            variable_type = variables.VariableType.INT
            literal = int(bool(left.literal and right.literal))
        elif op_token == TokenType.OR:
            variable_type = variables.VariableType.INT
            literal = int(bool(left.literal or right.literal))
        else:
            exit("Unknown binary token: {}".format(expr.operator_token))

        return variables.Value(variable_type, literal)

    # endregion


def identifier_from_token(token):
    return variables.Identifier(token.lexeme)


def value_from_token(token):
    mapping = {
        TokenType.INTEGER: variables.VariableType.INT,
        TokenType.FLOAT: variables.VariableType.FLOAT,
        TokenType.STRING: variables.VariableType.STRING,
    }

    variable_type = mapping.get(token.type)
    assert variable_type is not None, \
        "Can't map {} to variable type".format(token.type)

    return variables.Value(variable_type, token.literal)


def anonymous_identifier(value):
    assert value.variable_type == variables.VariableType.STRING, \
        "Only anonymous strings are allowed"

    name = "+{}".format(value.literal)
    return variables.Identifier(name)
