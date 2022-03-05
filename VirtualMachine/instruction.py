from enum import Enum, auto


class OpCode(Enum):
    PUSH = auto()
    PRINT = auto()
    READ = auto()
    WRITE = auto()

    NEG = auto()
    NOT = auto()

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    AND = auto()
    OR = auto()


class Instruction:

    def __init__(self, op_code):
        self.op_code = op_code


class NoLiteralInstruction(Instruction):

    def __init__(self, op_code):
        super().__init__(op_code)

    def __repr__(self):
        return "{}".format(self.op_code.name)


class LiteralInstruction(Instruction):

    def __init__(self, op_code, literal):
        super().__init__(op_code)
        self.literal = literal

    def __repr__(self):
        return "{} {}".format(self.op_code.name, self.literal)


def push_inst(literal):
    return LiteralInstruction(OpCode.PUSH, literal)
