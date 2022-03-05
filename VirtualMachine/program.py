import VirtualMachine.type_checker as tc
import VirtualMachine.instruction as inst
import VirtualMachine.variables as variables

from NarrativeLanguage.token import TokenType
from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor


class Program:

    def __init__(self, statements, type_checker: tc.TypeChecker):
        self.statements = statements
        self.type_checker = type_checker
        self.instructions = []

        self._transpiler = Visitor()
        self._transpiler.submit(statement.Print, self._transpile_print_stmt) \
            .submit(statement.Expression, self._transpile_expression_stmt) \
            .submit(statement.MacroDeclaration, self._transpile_macro_declaration_stmt) \
            .submit(statement.Assignment, self._transpile_assignment_stmt) \
            .submit(statement.Block, self._transpile_block_stmt) \
            .submit(statement.Condition, self._transpile_condition_stmt) \
            .submit(statement.Option, self._transpile_option_stmt)
        self._transpiler.submit(expression.Parenthesis, self._transpile_parenthesis_expr) \
            .submit(expression.Literal, self._transpile_literal_expr) \
            .submit(expression.Variable, self._transpile_variable_expr) \
            .submit(expression.SceneIdentifier, self._transpile_scene_identifier_expr) \
            .submit(expression.FunctionCall, self._transpile_function_call_expr) \
            .submit(expression.Unary, self._transpile_unary_expr) \
            .submit(expression.Binary, self._transpile_binary_expr)

    def transpile(self):
        for stmt in self.statements:
            self._transpiler.visit(stmt)

    def pretty_print(self):
        for i in range(len(self.instructions)):
            instruction = self.instructions[i]
            if instruction.op_code == inst.OpCode.PUSH:
                if not isinstance(instruction.literal, variables.VariableType):
                    continue

                i += 1
                offset_instruction = self.instructions[i]

                variable_type = instruction.literal
                offset = offset_instruction.literal
                variable = self.type_checker.variables[variable_type]._in_order[offset]

                representation = "({}) {}".format(
                    variable_type.name, variable.identifier)
                print(inst.push_inst(representation))
            else:
                print(instruction)

    def _add_instructions(self, instructions):
        if not isinstance(instructions, list):
            instructions = [instructions]

        self.instructions.extend(instructions)

    def _variable_instructions(self, identifier):
        # Variables are pushed into the stack like this
        # -- STACK --
        # Offset
        # Pointer

        variable = self.type_checker.read_variable(identifier)
        return ([
            inst.push_inst(variable.value.variable_type),
            inst.push_inst(variable.index)
        ])

    # region Statements

    def _transpile_print_stmt(self, stmt):
        pass

    def _transpile_expression_stmt(self, stmt):
        pass

    def _transpile_macro_declaration_stmt(self, stmt):
        pass

    def _transpile_assignment_stmt(self, stmt):
        # -- STACK --
        # Value to write
        # Variable

        self._transpiler.visit(stmt.assignment_expr)

        identifier = tc.identifier_from_token(stmt.identifier_token)

        instructions = self._variable_instructions(identifier)
        instructions.append(inst.NoLiteralInstruction(inst.OpCode.WRITE))
        self._add_instructions(instructions)

    def _transpile_block_stmt(self, stmt):
        pass

    def _transpile_condition_stmt(self, stmt):
        pass

    def _transpile_option_stmt(self, stmt):
        pass

    # endregion

    # region Expressions

    def _transpile_parenthesis_expr(self, expr):
        self._transpiler.visit(expr.inner_expr)

    def _transpile_literal_expr(self, expr):
        value = tc.value_from_token(expr.literal_token)
        self._add_instructions(inst.push_inst(value.literal))

    def _transpile_variable_expr(self, expr):
        # -- STACK --
        # Variable

        identifier = tc.identifier_from_token(expr.identifier_token)
        instructions = self._variable_instructions(identifier)
        instructions.append(inst.NoLiteralInstruction(inst.OpCode.READ))
        self._add_instructions(instructions)

    def _transpile_scene_identifier_expr(self, expr):
        pass

    def _transpile_function_call_expr(self, expr):
        pass

    def _transpile_unary_expr(self, expr):
        pass

    def _transpile_binary_expr(self, expr):
        # -- STACK --
        # Result of executing the left expression
        # Result of executing the right expression

        mapping = {
            TokenType.PLUS: inst.OpCode.ADD,
            TokenType.MINUS: inst.OpCode.SUB,
            TokenType.STAR: inst.OpCode.MUL,
            TokenType.SLASH: inst.OpCode.DIV,
            TokenType.EQUAL_EQUAL: inst.OpCode.EQ,
            TokenType.BANG_EQUAL: inst.OpCode.NEQ,
            TokenType.LESS: inst.OpCode.LT,
            TokenType.LESS_EQUAL: inst.OpCode.LTE,
            TokenType.GREATER: inst.OpCode.GT,
            TokenType.GREATER_EQUAL: inst.OpCode.GTE,
            TokenType.AND: inst.OpCode.AND,
            TokenType.OR: inst.OpCode.OR
        }

        op_code = mapping[expr.operator_token.type]
        self._transpiler.visit(expr.right_expr)
        self._transpiler.visit(expr.left_expr)
        self._add_instructions(inst.NoLiteralInstruction(op_code))

    # endregion
