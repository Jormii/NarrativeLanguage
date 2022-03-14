import numpy as np

import NarrativeLanguage.variables as variables


class VmField:

    def __init__(self):
        assert self._can_be_represented(), \
            "{} can't be represented".format(self)

    def _can_be_represented(self):
        raise NotImplementedError()

    def numpy_class(self):
        raise NotImplementedError()

    def size_in_bytes(self):
        return np.dtype(self.numpy_class()).itemsize

    def to_bytes(self):
        raise NotImplementedError()


class HeaderField(VmField):

    # Bits [31-16]: Instruction offset
    # Bits [15-8]: Stack size
    # Bits [7-0]: Options counter

    def __init__(self, instruction_offset, stack_size, options_counter):
        self.instruction_offset = instruction_offset
        self.stack_size = stack_size
        self.options_counter = options_counter

        super().__init__()

    def _can_be_represented(self):
        return can_be_represented_unsigned(self.instruction_offset, 16) and \
            can_be_represented_unsigned(self.stack_size, 8) and \
            can_be_represented_unsigned(self.options_counter, 8)

    def numpy_class(self):
        return np.uint32

    def to_bytes(self):
        inst_offset = self.instruction_offset << 16
        stack_size = self.stack_size << 8

        c = self.numpy_class()
        return c(inst_offset + stack_size + self.options_counter).tobytes()

    def __repr__(self):
        return "HEADER {}, {}".format(self.instruction_offset, self.options_counter)


class OptionField(VmField):

    # Bits [31-16]: String formatting PC
    # Bits [15-0]: Option instructions PC

    def __init__(self, string_pc, instructions_pc):
        self.string_pc = string_pc
        self.instructions_pc = instructions_pc

        super().__init__()

    def _can_be_represented(self):
        return can_be_represented_unsigned(self.string_pc, 16) and \
            can_be_represented_unsigned(self.instructions_pc, 16)

    def numpy_class(self):
        return np.uint32

    def to_bytes(self):
        string_pc = self.string_pc << 16
        return self.numpy_class()(string_pc + self.instructions_pc).tobytes()

    def __repr__(self):
        return "OPTION {}, {}".format(self.string_pc, self.instructions_pc)


class IntField(VmField):

    # Bits [31-24]: Store flag
    # Bits [23-0]: Integer

    def __init__(self, store_flag, literal):
        self.store_flag = int(store_flag)
        self.literal = literal

        super().__init__()

    def _can_be_represented(self):
        return can_be_represented_unsigned(self.literal, 24)

    def numpy_class(self):
        return np.uint32

    def to_bytes(self):
        store_flag = self.store_flag << 24
        return self.numpy_class()(store_flag + self.literal).tobytes()

    def __repr__(self):
        return "INT {}, {}".format(self.store_flag, self.literal)


class FloatField(VmField):

    def __init__(self, store_flag, literal):
        self.store_flag = np.uint8(store_flag)
        self.literal = variables.FLOAT_TYPE.numpy_type(literal)

        super().__init__()

        # TODO
        raise NotImplementedError()

    def to_bytes(self):
        return self.store_flag.tobytes() + self.literal.tobytes()

    def __repr__(self):
        return "FLOAT {}, {}".format(self.store_flag, self.literal)


class StringField(VmField):

    # UTF-16

    def __init__(self, string):
        self.string = (string + "\0").encode("utf-16")
        self.string = self.string[2:]   # Get rid of 0xFF and 0xFE
        a = len(self.string)
        b = len(string)

        super().__init__()

    def _can_be_represented(self):
        return True

    def size_in_bytes(self):
        return len(self.string)

    def to_bytes(self):
        return self.string

    def __repr__(self):
        return "STRING {}".format(self.string.decode("utf-16"))


class InstructionField(VmField):

    # Bits [31-24]: OpCode
    # Bits [23-0]: Literal

    def __init__(self, op_code, literal):
        self.op_code = op_code
        self.literal = literal

        super().__init__()

    def _can_be_represented(self):
        return can_be_represented_unsigned(self.op_code, 8) and \
            can_be_represented_signed(self.literal, 24)

    def numpy_class(self):
        return np.uint32

    def to_bytes(self):
        op_code = self.op_code << 24
        return self.numpy_class()(op_code + self.literal).tobytes()

    def __repr__(self):
        return "INST {}, {}".format(self.op_code, self.literal)


def can_be_represented_signed(number, n_bits):
    power = 2**(n_bits - 1)
    lower_bound = -power
    upper_bound = power - 1
    return number >= lower_bound and number <= upper_bound


def can_be_represented_unsigned(number, n_bits):
    lower_bound = 0
    upper_bound = 2**n_bits - 1
    return number >= lower_bound and number <= upper_bound


def _int_from_variable(variable):
    store_flag = variable.scope == variables.VariableScope.STORE
    literal = variable.value.literal

    return IntField(store_flag, literal)


def _float_from_variable(variable):
    store_flag = variable.scope == variables.VariableScope.STORE
    literal = variable.value.literal

    return FloatField(store_flag, literal)


def _string_from_variable(variable):
    string = variable.value.literal

    return StringField(string)


VALUE_TYPE_CALLBACKS = {
    variables.INT_TYPE: _int_from_variable,
    variables.FLOAT_TYPE: _float_from_variable,
    variables.STRING_TYPE: _string_from_variable
}
