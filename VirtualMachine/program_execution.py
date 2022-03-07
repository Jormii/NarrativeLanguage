from VirtualMachine.program import Program
from VirtualMachine.instruction import OpCode
from VirtualMachine.variables import VariableType
from VirtualMachine.type_checker import value_from_token, anonymous_identifier


class ProgramExecution:

    def __init__(self, program: Program):
        self.program = program
        self.max_stack_size = 0
        self.n_instructions = len(self.program.instructions)

        self._pc = 0
        self._stack = []
        self._executing = True
        self._type_checker = program.type_checker
        self._options_to_display = [False] * len(program._option_statements)

    def execute(self):
        self._execute_pc(0)
        try:
            while True:
                for index, display in enumerate(self._options_to_display):
                    if not display:
                        continue

                    option = self.program._option_statements[index]
                    value = value_from_token(option.string_token)
                    identifier = anonymous_identifier(value)
                    variable = self._type_checker.read_variable(identifier)
                    print("{}: {}".format(index, variable.value.literal))

                correct_input = False
                while not correct_input:
                    index = int(input("> "))
                    if index < 0 or index >= len(self._options_to_display):
                        continue

                    correct_input = self._options_to_display[index]

                pc = self.program._option_statements_pc[index]
                self._execute_pc(pc)
        except KeyboardInterrupt:
            pass

        # TODO: Force visiting all instructions to guarantee max stack size is
        # the actual maximum
        print("\n\nInstruction count: {}\nMax stack size: {}".format(
            self.n_instructions, self.max_stack_size))

    def _execute_pc(self, pc):
        mapping = {
            OpCode.PUSH: self._push_inst,
            OpCode.POP: self._pop_inst,
            OpCode.PRINT: self._print_inst,
            OpCode.DISPLAY: self._display_inst,
            OpCode.READ: self._read_inst,
            OpCode.WRITE: self._write_inst,
            OpCode.IJUMP: self._ijump_inst,
            OpCode.CJUMP: self._cjump_inst,

            OpCode.CALL: self._call_inst,

            OpCode.NEG: self._neg_inst,
            OpCode.NOT: self._not_inst,

            OpCode.ADD: self._add_inst,
            OpCode.SUB: self._sub_inst,
            OpCode.MUL: self._mul_inst,
            OpCode.DIV: self._div_inst,
            OpCode.EQ: self._eq_inst,
            OpCode.NEQ: self._neq_inst,
            OpCode.LT: self._lt_inst,
            OpCode.LTE: self._lte_inst,
            OpCode.GT: self._gt_inst,
            OpCode.GTE: self._gte_inst,
            OpCode.AND: self._and_inst,
            OpCode.OR: self._or_inst,

            OpCode.EOX: self._eox_inst
        }

        self._pc = pc
        self._executing = True
        while self._executing:
            inst = self.program.instructions[self._pc]
            mapping[inst.op_code](inst)
            self._pc += 1

        assert len(self._stack) == 0

    def _push(self, literal):
        self._stack.append(literal)
        self.max_stack_size = max(self.max_stack_size, len(self._stack))

    def _pop(self):
        return self._stack.pop(-1)

    def _push_inst(self, inst):
        self._push(inst.literal)

    def _pop_inst(self, inst):
        self._pop()

    def _print_inst(self, inst):
        index = inst.literal
        strings = self._type_checker.variables[VariableType.STRING]
        variable = strings._in_order[index]

        print(variable.value.literal)

    def _display_inst(self, inst):
        index = inst.literal
        self._options_to_display[index] = True

    def _read_inst(self, inst):
        index = self._pop()
        variable_type = self._pop()

        variables = self._type_checker.variables[variable_type]
        variable = variables._in_order[index]

        self._push(variable.value.literal)

    def _write_inst(self, inst):
        index = self._pop()
        variable_type = self._pop()
        literal = self._pop()

        variables = self._type_checker.variables[variable_type]
        variable = variables._in_order[index]

        old_value = variable.value.literal

        variable.value.literal = literal

        print("({}) {} = {} <- {}".format(
            variable_type.name, variable.identifier, old_value, literal))

    def _ijump_inst(self, inst):
        self._pc = inst.literal

    def _cjump_inst(self, inst):
        value = self._pop()
        if not bool(value):
            self._pc = inst.literal

    def _call_inst(self, inst):
        identifier = self._pop()
        n_args = self._pop()
        args = []
        for _ in range(n_args):
            args.append(self._pop())

        function = self._type_checker.function_prototypes.get(identifier)
        return_value = function.call(args)
        self._push(return_value)

        print("{}() -> {}".format(identifier, return_value))

    def _neg_inst(self, inst):
        value = self._pop()
        self._push(-value)

    def _not_inst(self, inst):
        value = self._pop()
        self._push(int(not bool(value)))

    def _add_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(left_value + right_value)

    def _sub_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(left_value - right_value)

    def _mul_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(left_value * right_value)

    def _div_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        div = left_value / right_value
        t = type(left_value)
        self._push(t(div))

    def _eq_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(left_value == right_value))

    def _neq_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(left_value != right_value))

    def _lt_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(left_value < right_value))

    def _lte_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(left_value <= right_value))

    def _gt_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(left_value >= right_value))

    def _gte_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(left_value >= right_value))

    def _and_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(bool(left_value and right_value)))

    def _or_inst(self, inst):
        left_value = self._pop()
        right_value = self._pop()

        self._push(int(bool(left_value or right_value)))

    def _eox_inst(self, inst):
        self._executing = False
