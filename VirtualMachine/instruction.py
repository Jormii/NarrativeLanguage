from enum import Enum, auto


class OpCode(Enum):
    PUSH = auto()
    POP = auto()
    PRINT = auto()
    PRINTI = auto()     # Prints number in stack
    PRINTS = auto()     # Prints string pointer in stack
    PRINTSL = auto()    # Prints string variable. Offset is instruction's literal
    ENDL = auto()
    DISPLAY = auto()
    SWITCH = auto()     # Loads a new scene
    READ = auto()
    WRITE = auto()
    READG = auto()      # Read global
    WRITEG = auto()     # Write global
    IJUMP = auto()
    CJUMP = auto()  # Jumps if condition evaluates to False

    CALL = auto()

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

    EOX = auto()    # End of execution


STACK_MODIFICATION = {
    OpCode.PUSH: 1,
    OpCode.POP: -1,
    OpCode.PRINT: 0,
    OpCode.PRINTI: -1,
    OpCode.PRINTS: -1,
    OpCode.PRINTSL: 0,
    OpCode.ENDL: 0,
    OpCode.DISPLAY: 0,
    OpCode.SWITCH: 0,
    OpCode.READ: 1,
    OpCode.WRITE: -1,
    OpCode.READG: 1,
    OpCode.WRITEG: -1,
    OpCode.IJUMP: 0,
    OpCode.CJUMP: -1,

    # OpCode.CALL: None,    Call depends on number of arguments

    OpCode.NEG: 0,
    OpCode.NOT: 0,

    OpCode.ADD: -1,
    OpCode.SUB: -1,
    OpCode.MUL: -1,
    OpCode.DIV: -1,
    OpCode.EQ: -1,
    OpCode.NEQ: -1,
    OpCode.LT: -1,
    OpCode.LTE: -1,
    OpCode.GT: -1,
    OpCode.GTE: -1,
    OpCode.AND: -1,
    OpCode.OR: -1,

    OpCode.EOX: 0
}


class Instruction:

    def __init__(self, op_code):
        self.op_code = op_code

    def get_literal(self):
        raise NotImplementedError()


class NoLiteralInstruction(Instruction):

    def __init__(self, op_code):
        super().__init__(op_code)

    def get_literal(self):
        return 0

    def __repr__(self):
        return "{}".format(self.op_code.name)


class LiteralInstruction(Instruction):

    def __init__(self, op_code, literal):
        super().__init__(op_code)
        self.literal = literal

    def get_literal(self):
        return self.literal

    def __repr__(self):
        return "{} {}".format(self.op_code.name, self.literal)


def push_inst(literal):
    return LiteralInstruction(OpCode.PUSH, literal)
