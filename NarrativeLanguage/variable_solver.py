import NarrativeLanguage.variables as variables
from NarrativeLanguage.token import TokenType
from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor
from NarrativeLanguage.constexpr_interpreter import CONSTEXPR_INTERPRETER, NotConstExprException


class VariableSolver:

    def __init__(self, scene_mapping, statements, global_variables, function_prototypes):
        self.scene_mapping = scene_mapping
        self.statements = statements
        self.global_variables = global_variables
        self.function_prototypes = function_prototypes
        self.variables = variables.Variables()

        self._solver = Visitor()
        self._solver.submit(statement.Print, self._solve_print_stmt) \
            .submit(statement.Expression, self._solve_expression_stmt) \
            .submit(statement.GlobalDeclaration, self._solve_global_declaration_stmt) \
            .submit(statement.GlobalDefinition, self._solve_global_definition_stmt) \
            .submit(statement.Store, self._solve_store_stmt) \
            .submit(statement.Assignment, self._solve_assignment_stmt) \
            .submit(statement.Block, self._solve_block_stmt) \
            .submit(statement.Condition, self._solve_condition_stmt) \
            .submit(statement.Option, self._solve_option_stmt) \
            .submit(statement.SceneSwitch, self._solve_scene_switch_stmt)
        self._solver.submit(expression.Parenthesis, self._solve_parenthesis_expr) \
            .submit(expression.Literal, self._solve_literal_expr) \
            .submit(expression.Variable, self._solve_variable_expr) \
            .submit(expression.FunctionCall, self._solve_function_call_expr) \
            .submit(expression.Unary, self._solve_unary_expr) \
            .submit(expression.Binary, self._solve_binary_expr)

        CONSTEXPR_INTERPRETER.solver = self

    def solve(self):
        for stmt in self.statements:
            self._solver.visit(stmt)

        self.variables.sort()

    def is_defined(self, identifier):
        return self.variables.is_defined(identifier)

    def define(self, scope, identifier, value, line_declaration):
        self.variables.define(scope, identifier, value, line_declaration)

    def read(self, identifier):
        variable = self.variables.read(identifier)
        if variable.scope in [variables.VariableScope.GLOBAL_DEFINE,
                              variables.VariableScope.GLOBAL_DECLARE]:
            return self.global_variables.read(identifier)

        return variable

    def _handle_global(self, scope, identifier, value):
        if not self.global_variables.is_defined(identifier):

            self.global_variables.define(scope, identifier, value)
            return

        variable = self.global_variables.read(identifier)
        if variable.scope == variables.VariableScope.GLOBAL_DEFINE and \
                scope == variables.VariableScope.GLOBAL_DEFINE:
            exit("GLOBAL variable {} already defined in another file".format(identifier))

        if variable.scope == variables.VariableScope.GLOBAL_DECLARE and \
                scope == variables.VariableScope.GLOBAL_DEFINE:
            self.global_variables.define(scope, identifier, value)
            v = self.global_variables.read(identifier)
            v.index = variable.index


# region Statements


    def _solve_print_stmt(self, stmt):
        value = value_from_token(stmt.string_token)
        identifier = anonymous_identifier(value)
        if not self.is_defined(identifier):
            token = stmt.string_token
            line_declaration = (token.line, token.column)
            self.define(variables.VariableScope.TEMPORAL,
                        identifier, value, line_declaration)

    def _solve_expression_stmt(self, stmt):
        self._solver.visit(stmt.expr)

    def _solve_global_declaration_stmt(self, stmt):
        identifier = identifier_from_token(stmt.identifier_token)

        assert not self.is_defined(identifier), \
            "GLOBAL variable {} already defined/declared".format(identifier)

        scope = variables.VariableScope.GLOBAL_DECLARE
        value = variables.Value(variables.INT_TYPE, 0)
        self.define(scope, identifier, value)
        self._handle_global(scope, identifier, value)

    def _solve_global_definition_stmt(self, stmt):
        assignment_stmt = stmt.assignment_stmt
        identifier = identifier_from_token(assignment_stmt.identifier_token)
        value = CONSTEXPR_INTERPRETER.visit(assignment_stmt.assignment_expr)

        assert not self.is_defined(identifier), \
            "GLOBAL variable '{}' already defined/declared".format(identifier)

        scope = variables.VariableScope.GLOBAL_DEFINE
        self.define(scope, identifier, value)
        self._handle_global(scope, identifier, value)

    def _solve_store_stmt(self, stmt):
        assignment_stmt = stmt.assignment_stmt
        identifier = identifier_from_token(assignment_stmt.identifier_token)
        value = CONSTEXPR_INTERPRETER.visit(assignment_stmt.assignment_expr)

        assert not self.is_defined(identifier), \
            "STORE variable '{}' already defined".format(identifier)

        token = stmt.assignment_stmt.identifier_token
        line_declaration = (token.line, token.column)
        self.define(variables.VariableScope.STORE,
                    identifier, value, line_declaration)

    def _solve_assignment_stmt(self, stmt):
        identifier = identifier_from_token(stmt.identifier_token)
        try:
            value = CONSTEXPR_INTERPRETER.visit(stmt.assignment_expr)
        except NotConstExprException:
            value = self._solver.visit(stmt.assignment_expr)

        assert value.value_type not in [variables.STRING_TYPE, variables.STRING_PTR_TYPE], \
            "Can't store strings"

        if self.is_defined(identifier):
            variable = self.read(identifier)
            assert value.value_type == variable.value.value_type, \
                "Variable '{}' types aren't compatible".format(identifier)
        else:
            # None is used to indicate the variable holds a non-constant value
            #   and therefore we need to execute the given instructions
            token = stmt.identifier_token
            line_declaration = (token.line, token.column)
            self.define(variables.VariableScope.TEMPORAL,
                        identifier, value, line_declaration)

    def _solve_block_stmt(self, stmt):
        for inner_stmt in stmt.statements:
            self._solver.visit(inner_stmt)

    def _solve_condition_stmt(self, stmt):
        self._solver.visit(stmt.if_condition)
        self._solver.visit(stmt.if_block)

        for condition, block in zip(stmt.elifs_conditions, stmt.elifs_blocks):
            self._solver.visit(condition)
            self._solver.visit(block)

        if stmt.else_block is not None:
            self._solver.visit(stmt.else_block)

    def _solve_option_stmt(self, stmt):
        value = value_from_token(stmt.string_token)
        identifier = anonymous_identifier(value)
        if not self.is_defined(identifier):
            token = stmt.string_token
            line_declaration = (token.line, token.column)
            self.define(variables.VariableScope.TEMPORAL,
                        identifier, value, line_declaration)

        self._solver.visit(stmt.block_stmt)

    def _solve_scene_switch_stmt(self, stmt):
        identifier = identifier_from_token(stmt.scene_identifier_token)
        assert identifier.name in self.scene_mapping, \
            "Unknown scene '{}'".format(identifier)

    # endregion

    # region Expressions

    def _solve_parenthesis_expr(self, expr):
        return self._solver.visit(expr.inner_expr)

    def _solve_literal_expr(self, expr):
        assert expr.literal_token.type != TokenType.STRING, \
            "String literals aren't allowed"

        # TODO: Remove this later
        assert expr.literal_token.type != TokenType.FLOAT, \
            "Floats aren't allowed for now"

        return value_from_token(expr.literal_token)

    def _solve_variable_expr(self, expr):
        identifier = identifier_from_token(expr.identifier_token)
        assert self.is_defined(identifier), \
            "Variable {} isn't defined".format(identifier)

        variable = self.read(identifier)
        return variable.value

    def _solve_function_call_expr(self, expr):
        identifier = identifier_from_token(expr.identifier_token)
        assert self.function_prototypes.is_defined(identifier), \
            "Unknown function '{}'".format(identifier)

        args = []
        for arg_expr in expr.arguments:
            args.append(self._solver.visit(arg_expr))

        prototype = self.function_prototypes.get(identifier)
        assert prototype.compatible_args(args), \
            "Provided arguments aren't compatible with function {}. Provided: {}".format(
                prototype, args)

        prototype.called = True

        # None to indicate unknown value
        return variables.Value(prototype.return_type, None)

    def _solve_unary_expr(self, expr):
        value = self._solver.visit(expr.expr)
        assert value.value_type not in [variables.STRING_TYPE, variables.STRING_PTR_TYPE], \
            "Can't perform operations on strings"

        return value

    def _solve_binary_expr(self, expr):
        left_value = self._solver.visit(expr.left_expr)
        right_value = self._solver.visit(expr.right_expr)
        assert left_value.value_type == right_value.value_type, \
            "Values {} and {} aren't congruent".format(left_value, right_value)

        assert left_value.value_type not in [variables.STRING_TYPE, variables.STRING_PTR_TYPE], \
            "Can't perform operations on strings"

        return variables.Value(left_value.value_type, 0)

    # endregion


def identifier_from_token(token):
    return variables.Identifier(token.lexeme)


def value_from_token(token):
    mapping = {
        TokenType.INTEGER: variables.INT_TYPE,
        TokenType.FLOAT: variables.FLOAT_TYPE,
        TokenType.STRING: variables.STRING_TYPE
    }

    value_type = mapping.get(token.type)
    assert value_type is not None, \
        "Can't map {} to value type".format(token.type)

    return variables.Value(value_type, token.literal)


def anonymous_identifier(value):
    assert isinstance(value.literal, str), \
        "Only anonymous strings are allowed"

    name = "+{}".format(value.literal)
    return variables.Identifier(name)
