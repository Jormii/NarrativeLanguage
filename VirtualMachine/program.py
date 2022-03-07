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

        self._option_statements = []
        self._option_statements_pc = []
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

        self._add_instructions(inst.NoLiteralInstruction(inst.OpCode.EOX))

        # Option statements are added to the end of the program
        i = 0
        while i < len(self._option_statements):
            stmt = self._option_statements[i]
            self._option_statements_pc.append(len(self.instructions))
            self._transpiler.visit(stmt.block_stmt)
            self._add_instructions(inst.NoLiteralInstruction(inst.OpCode.EOX))

            i += 1

    def pretty_print(self):
        pc = 0
        while pc < len(self.instructions):
            instruction = self.instructions[pc]
            pushes_variable = instruction.op_code == inst.OpCode.PUSH and \
                isinstance(instruction.literal, variables.VariableType)
            pushes_function = instruction.op_code == inst.OpCode.PUSH and \
                isinstance(instruction.literal, variables.Identifier)
            if pushes_variable:
                pc += 1
                offset_instruction = self.instructions[pc]

                variable_type = instruction.literal
                offset = offset_instruction.literal
                variable = self.type_checker.variables[variable_type]._in_order[offset]

                representation = "({}) {}".format(
                    variable_type.name, variable.identifier)
                print("{}: {}".format(pc - 1, representation))
            elif pushes_function:
                print("{}: {}()".format(pc, instruction))
            else:
                print("{}: {}".format(pc, instruction))

            pc += 1

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
        value = tc.value_from_token(stmt.string_token)
        identifier = tc.anonymous_identifier(value)
        variable = self.type_checker.read_variable(identifier)

        literal = variable.index
        self._add_instructions(
            inst.LiteralInstruction(inst.OpCode.PRINT, literal))

    def _transpile_expression_stmt(self, stmt):
        if not isinstance(stmt.expr, expression.FunctionCall):
            # Only function calls may have impact on the program
            return

        self._transpile_function_call_expr(stmt.expr)

        # Pop stack to discard return value
        self._add_instructions(inst.NoLiteralInstruction(inst.OpCode.POP))

    def _transpile_macro_declaration_stmt(self, stmt):
        # Macros have no effect on the program
        return

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

            jump_instruction.literal = pc - 1
            # PC - 1 because PC will be incremented during execution

    def _transpile_option_stmt(self, stmt):
        literal = len(self._option_statements)
        self._add_instructions(
            inst.LiteralInstruction(inst.OpCode.DISPLAY, literal))
        self._option_statements.append(stmt)

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
        is_macro = expr.variable_type == expression.Variable.VariableType.MACRO
        if is_macro:
            self._transpile_macro_as_literal(expr.identifier_token)
            return

        instructions = self._variable_instructions(identifier)
        instructions.append(inst.NoLiteralInstruction(inst.OpCode.READ))
        self._add_instructions(instructions)

    def _transpile_macro_as_literal(self, identifier_token):
        mapping = {
            variables.VariableType.INT: TokenType.INTEGER,
            variables.VariableType.FLOAT: TokenType.FLOAT,
            variables.VariableType.STRING: TokenType.STRING
        }

        identifier = tc.identifier_from_token(identifier_token)
        variable = self.type_checker.read_macro(identifier)

        token = identifier_token.copy()
        token.type = mapping[variable.value.variable_type]
        token.literal = variable.value.literal

        literal_expr = expression.Literal(token)
        self._transpile_literal_expr(literal_expr)

    def _transpile_scene_identifier_expr(self, expr):
        pass

    def _transpile_function_call_expr(self, expr):
        # -- STACK --
        # Function ptr
        # N args
        # Arg0
        # Arg1
        # ...
        # ArgN-1

        for arg_expr in reversed(expr.arguments):
            self._transpiler.visit(arg_expr)
        self._add_instructions([
            inst.push_inst(len(expr.arguments)),
            inst.push_inst(tc.identifier_from_token(expr.identifier_token)),
            inst.NoLiteralInstruction(inst.OpCode.CALL)
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
