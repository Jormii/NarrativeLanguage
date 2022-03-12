import NarrativeLanguage.variable_solver as vs
import NarrativeLanguage.variables as variables

from NarrativeLanguage.token import TokenType
from NarrativeLanguage import expression, statement
from NarrativeLanguage.visitor import Visitor

import VirtualMachine.types as types
import VirtualMachine.instruction as inst


class YieldInstruction(inst.Instruction):

    def __init__(self, op_code, identifier):
        super().__init__(op_code)
        self.identifier = identifier

    def unwrap(self):
        raise NotImplementedError()


class Offsets:

    class OffsetInstruction(YieldInstruction):

        def __init__(self, op_code, identifier, offsets):
            super().__init__(op_code, identifier)
            self.offsets = offsets

        def unwrap(self):
            offset = self.offsets.variables_offset[self.identifier]
            return inst.LiteralInstruction(self.op_code, offset)

    def __init__(self):
        self.offset = 0
        self.variables_offset = {}
        self.used_variables = set()

    def calculate_offsets(self, solver: vs.VariableSolver):
        # Group variables by type
        by_type = {}
        for variable in solver.variables._in_order:
            if variable.scope in [variables.VariableScope.GLOBAL_DEFINE,
                                  variables.VariableScope.GLOBAL_DECLARE]:
                # Ignore global variables
                continue

            value_type = variable.value.value_type
            if value_type not in by_type:
                by_type[value_type] = []
            by_type[value_type].append(variable)

        # Calculate offsets
        custom_order = [variables.INT_TYPE, variables.FLOAT_TYPE,
                        variables.STRING_TYPE]
        for value_type in custom_order:
            type_variables = by_type.get(value_type, [])
            cb = types.VALUE_TYPE_CALLBACKS[value_type]

            for variable in type_variables:
                if not variable.identifier in self.used_variables:
                    continue

                field = cb(variable)

                self.variables_offset[variable.identifier] = self.offset
                self.offset += field.size_in_bytes()

    def wrap_instruction(self, op_code, identifier):
        self.used_variables.add(identifier)
        return Offsets.OffsetInstruction(op_code, identifier, self)


class Option:

    def __init__(self, string_identifier, block_stmt, offset):
        self.string_identifier = string_identifier
        self.block_stmt = block_stmt
        self.offset = offset
        self.pc = None


class Program:

    def __init__(self, statements, solver: vs.VariableSolver):
        self.statements = statements
        self.solver = solver

        self.base_offset = types.OffsetField(0).size_in_bytes()
        self.instructions = []
        self.offsets = Offsets()
        self.options = []

        self._transpiler = Visitor()
        self._transpiler.submit(statement.Print, self._transpile_print_stmt) \
            .submit(statement.Expression, self._transpile_expression_stmt) \
            .submit(statement.GlobalDeclaration, self._transpile_global_declaration_stmt) \
            .submit(statement.GlobalDefinition, self._transpile_global_definition_stmt) \
            .submit(statement.Store, self._transpile_store_stmt) \
            .submit(statement.Assignment, self._transpile_assignment_stmt) \
            .submit(statement.Block, self._transpile_block_stmt) \
            .submit(statement.Condition, self._transpile_condition_stmt) \
            .submit(statement.Option, self._transpile_option_stmt) \
            .submit(statement.OptionVisibility, self._transpile_option_visibility_stmt)
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

        self._add_instructions(inst.NoLiteralInstruction(inst.OpCode.EOX))

        # Option statements are added to the end of the program
        i = 0
        while i < len(self.options):
            option = self.options[i]
            option.pc = len(self.instructions)

            self._transpiler.visit(option.block_stmt)
            self._add_instructions(inst.NoLiteralInstruction(inst.OpCode.EOX))

            i += 1

        # Replace YieldInstruction instructions
        self.offsets.offset = self.base_offset + \
            len(self.options) * types.OptionField(0, 0).size_in_bytes()

        self.offsets.calculate_offsets(self.solver)
        for i, instruction in enumerate(self.instructions):
            if not isinstance(instruction, YieldInstruction):
                continue

            self.instructions[i] = instruction.unwrap()

    def pretty_print(self):
        print("\n-- VARIABLES --")
        for identifier, offset in self.offsets.variables_offset.items():
            print("{}: {}".format(offset, identifier))

        print("\n-- OPTIONS --")
        for option in self.options:
            print("{}: {} - {}".format(option.offset,
                  option.pc, option.string_identifier))

        print("\n-- INSTRUCTIONS --")
        for pc, instruction in enumerate(self.instructions):
            print("{}: {}".format(pc, instruction))

    def _add_instructions(self, instructions):
        if not isinstance(instructions, list):
            instructions = [instructions]

        self.instructions.extend(instructions)

    # region Statements

    def _transpile_print_stmt(self, stmt):
        value = vs.value_from_token(stmt.string_token)
        identifier = vs.anonymous_identifier(value)

        self._add_instructions(
            self.offsets.wrap_instruction(inst.OpCode.PRINT, identifier))

    def _transpile_expression_stmt(self, stmt):
        if not isinstance(stmt.expr, expression.FunctionCall):
            # Only function calls may have impact on the program
            return

        self._transpile_function_call_expr(stmt.expr)

        # Pop stack to discard return value
        self._add_instructions(inst.NoLiteralInstruction(inst.OpCode.POP))

    def _transpile_global_declaration_stmt(self, stmt):
        # This statement doesn't affect the execution of the program
        return

    def _transpile_global_definition_stmt(self, stmt):
        # This statement doesn't affect the execution of the program
        return

    def _transpile_store_stmt(self, stmt):
        # This statement doesn't affect the execution of the program
        return

    def _transpile_assignment_stmt(self, stmt):
        # -- STACK --
        # Value to write

        self._transpiler.visit(stmt.assignment_expr)

        identifier = vs.identifier_from_token(stmt.identifier_token)
        self._add_instructions(
            self.offsets.wrap_instruction(inst.OpCode.WRITE, identifier))

    def _transpile_block_stmt(self, stmt):
        for stmt in stmt.statements:
            self._transpiler.visit(stmt)

    def _transpile_condition_stmt(self, stmt):
        all_conditions = [stmt.if_condition]
        all_conditions.extend(stmt.elifs_conditions)
        all_blocks = [stmt.if_block]
        all_blocks.extend(stmt.elifs_blocks)

        pcs = []    # PC for end of blocks
        jump_instructions = []
        for i, (cond, block) in enumerate(zip(all_conditions, all_blocks)):
            self._transpiler.visit(cond)
            conditional_jump = inst.LiteralInstruction(inst.OpCode.CJUMP, 0)
            self._add_instructions(conditional_jump)
            jump_instructions.append((i, conditional_jump))

            self._transpiler.visit(block)

            is_last = (i + 1) == len(all_blocks)
            if not is_last or stmt.else_block is not None:
                inconditional_jump = inst.LiteralInstruction(
                    inst.OpCode.IJUMP, 0)
                self._add_instructions(inconditional_jump)
                jump_instructions.append((i, inconditional_jump))

            pcs.append(len(self.instructions))

        if stmt.else_block is not None:
            self._transpiler.visit(stmt.else_block)
            pcs.append(len(self.instructions))

        for block_index, jump_instruction in jump_instructions:
            if jump_instruction.op_code == inst.OpCode.CJUMP:
                pc = pcs[block_index]  # Beginning of next block
            else:
                pc = pcs[-1]  # End of all blocks

            # PC - 1 because PC will be incremented during execution
            jump_instruction.literal = pc - 1

    def _transpile_option_stmt(self, stmt):
        value = vs.value_from_token(stmt.string_token)
        identifier = vs.anonymous_identifier(value)

        offset = self.base_offset + \
            len(self.options) * types.OptionField(0, 0).size_in_bytes()
        option = Option(identifier, stmt.block_stmt, offset)

        self.options.append(option)
        self._add_instructions(
            inst.LiteralInstruction(inst.OpCode.DISPLAY, offset))

    def _transpile_option_visibility_stmt(self, stmt):
        # TODO: Remove DISPLAY and HIDE keywords
        raise NotImplementedError()
        mapping = {
            TokenType.DISPLAY: inst.OpCode.DISPLAY,
            TokenType.HIDE: inst.OpCode.HIDE
        }

        action_token = stmt.action_token
        value = vs.value_from_token(stmt.string_token)
        identifier = vs.anonymous_identifier(value)
        index = self._option_indices[identifier]

        op_code = mapping[action_token.type]
        self._add_instructions(inst.LiteralInstruction(op_code, index))

    # endregion

    # region Expressions

    def _transpile_parenthesis_expr(self, expr):
        self._transpiler.visit(expr.inner_expr)

    def _transpile_literal_expr(self, expr):
        value = vs.value_from_token(expr.literal_token)
        self._add_instructions(inst.push_inst(value.literal))

    def _transpile_variable_expr(self, expr):
        identifier = vs.identifier_from_token(expr.identifier_token)
        self._add_instructions(
            self.offsets.wrap_instruction(inst.OpCode.READ, identifier))

    def _transpile_scene_identifier_expr(self, expr):
        raise NotImplementedError()

    def _transpile_function_call_expr(self, expr):
        # -- STACK --
        # Offset to store
        # N args
        # Arg0
        # Arg1
        # ...
        # ArgN-1

        identifier = vs.identifier_from_token(expr.identifier_token)
        hash = vs.string_32b_hash(identifier.name)

        for arg_expr in reversed(expr.arguments):
            self._transpiler.visit(arg_expr)
        self._add_instructions([
            inst.push_inst(len(expr.arguments)),
            inst.LiteralInstruction(inst.OpCode.CALL, hash)
        ])

    def _transpile_unary_expr(self, expr):
        # -- STACK --
        # Result of executing the expression

        mapping = {
            TokenType.MINUS: inst.OpCode.NEG,
            TokenType.BANG: inst.OpCode.NOT
        }

        op_code = mapping[expr.operator_token.type]
        self._transpiler.visit(expr.expr)
        self._add_instructions(inst.NoLiteralInstruction(op_code))

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
