from VirtualMachine.program import Program
from VirtualMachine.instruction import OpCode


class ProgramExecution:

    def __init__(self, program: Program):
        self.program = program
        self.max_stack_size = 0
        self.n_instructions = len(self.program.instructions)

        self._stack = []
        self._type_checker = program.type_checker

    def execute(self):
        mapping = {
            OpCode.PUSH: self._push_inst,
            OpCode.READ: self._read_inst,
            OpCode.WRITE: self._write_inst,
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
            OpCode.OR: self._or_inst
        }

        for inst in self.program.instructions:
            mapping[inst.op_code](inst)

        assert len(self._stack) == 0

        print("Instruction count: {}\nMax stack size: {}".format(
            self.n_instructions, self.max_stack_size))

    def _push(self, literal):
        self._stack.append(literal)
        self.max_stack_size = max(self.max_stack_size, len(self._stack))

    def _pop(self):
        return self._stack.pop(-1)

    def _push_inst(self, inst):
        self._push(inst.literal)

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
