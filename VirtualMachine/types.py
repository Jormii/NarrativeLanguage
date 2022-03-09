import numpy as np

import NarrativeLanguage.variables as variables


class VmField:

    def size_in_bytes(self):
        raise NotImplementedError()


class OffsetField(VmField):

    def __init__(self, literal):
        self.literal = variables.INT_TYPE.numpy_type(literal)

    def size_in_bytes(self):
        return self.literal.itemsize


class IntField(VmField):

    def __init__(self, store_flag, literal):
        self.store_flag = np.uint8(store_flag)
        self.literal = variables.INT_TYPE.numpy_type(literal)

    def size_in_bytes(self):
        return self.store_flag.itemsize + self.literal.itemsize


class FloatField(VmField):

    def __init__(self, store_flag, literal):
        self.store_flag = np.uint8(store_flag)
        self.literal = variables.FLOAT_TYPE.numpy_type(literal)

    def size_in_bytes(self):
        return self.store_flag.itemsize + self.literal.itemsize


class StringField(VmField):

    def __init__(self, string):
        self.char_dtype = variables.STRING_TYPE.numpy_dtype
        self.string = string.encode("utf-16")

    def size_in_bytes(self):
        return self.char_dtype.itemsize * len(self.string)


class OptionField(VmField):

    def __init__(self, string_offset, pc):
        self.string_offset = variables.INT_TYPE.numpy_type(string_offset)
        self.pc = variables.INT_TYPE.numpy_type(pc)

    def size_in_bytes(self):
        return self.string_offset.itemsize + self.pc.itemsize


class InstructionField(VmField):

    def __init__(self, op_code, literal):
        self.op_code = np.uint8(op_code)
        self.literal = np.int32(literal)

    def size_in_bytes(self):
        return self.op_code.itemsize + self.literal.itemsize


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
