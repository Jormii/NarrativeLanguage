import os

import numpy as np


from VirtualMachine.program import Program
from VirtualMachine.variables import VariableType
from VirtualMachine.type_checker import value_from_token, anonymous_identifier
import VirtualMachine.instruction as inst


class ProgramBinary:

    class Field:

        def to_binary(self):
            raise NotImplementedError()

    class Metadata(Field):

        def __init__(self, n_ints, n_floats, n_strings, n_options, n_instructions):
            self.n_ints = n_ints
            self.n_floats = n_floats
            self.n_strings = n_strings
            self.n_options = n_options
            self.n_instructions = n_instructions

        def to_binary(self):
            return np.array([
                self.n_ints, self.n_floats, self.n_strings,
                self.n_options, self.n_instructions], dtype=np.uint32).tobytes()

    class Integer(Field):

        def __init__(self, value):
            self.value = np.int32(value)

        def to_binary(self):
            return self.value.tobytes()

    class Float(Field):

        def __init__(self, value):
            self.value = np.float32(value)

        def to_binary(self):
            return self.value.tobytes()

    class String(Field):

        def __init__(self, string):
            self.string = string

        def to_binary(self):
            length_bytes = np.uint32(len(self.string) + 1).tobytes()
            string_bytes = bytearray(self.string.encode("utf-16"))

            return length_bytes + string_bytes

    class Option(Field):

        def __init__(self, string_index, pc):
            self.string_index = string_index
            self.pc = pc

        def to_binary(self):
            index_bytes = np.uint32(self.string_index).tobytes()
            pc_bytes = np.uint32(self.pc).tobytes()

            return index_bytes + pc_bytes

    class Instruction(Field):

        def __init__(self, op_code, literal):
            self.op_code = op_code

            if isinstance(literal, VariableType):
                # -1 because enum.auto() starts at 1
                self.literal = literal.value - 1
            else:
                self.literal = literal

        def to_binary(self):
            # -1 because enum.auto() starts at 1
            op_code_bytes = np.uint8(self.op_code.value - 1).tobytes()
            literal_bytes = np.int32(self.literal).tobytes()

            return op_code_bytes + literal_bytes

    def __init__(self, program: Program):
        self.program = program
        self._type_checker = program.type_checker

        self._metadata = None
        self._fields = []

    def write_to_file(self, path):
        head, tail = os.path.split(path)

        assert len(tail) != 0, "Path doesn't describe a file"
        if not os.path.exists(head):
            os.makedirs(head)

        # Metadata
        self._metadata = ProgramBinary.Metadata(
            self._type_checker.variables[VariableType.INT].length(),
            self._type_checker.variables[VariableType.FLOAT].length(),
            self._type_checker.variables[VariableType.STRING].length(),
            len(self.program._option_statements),
            len(self.program.instructions)
        )

        # Fields
        self._parse_ints()
        self._parse_floats()
        self._parse_strings()
        self._parse_options()
        self._parse_instructions()

        # Dump to file
        with open(path, "wb") as out_f:
            out_f.write(self._metadata.to_binary())
            for field in self._fields:
                for e in field:
                    bytes = e.to_binary()
                    out_f.write(bytes)

        print("{}: {}".format(path, os.path.getsize(path)))

    def _parse_ints(self):
        ints = self._type_checker.variables[VariableType.INT]
        written_ints = []
        for i in range(self._metadata.n_ints):
            variable = ints._in_order[i]
            literal = variable.value.literal
            written_ints.append(ProgramBinary.Integer(literal))

        self._fields.append(written_ints)

    def _parse_floats(self):
        floats = self._type_checker.variables[VariableType.FLOAT]
        written_floats = []
        for i in range(self._metadata.n_floats):
            variable = floats._in_order[i]
            literal = variable.value.literal
            written_floats.append(ProgramBinary.Float(literal))

        self._fields.append(written_floats)

    def _parse_strings(self):
        strings = self._type_checker.variables[VariableType.STRING]
        written_strings = []
        for i in range(self._metadata.n_strings):
            variable = strings._in_order[i]
            literal = variable.value.literal
            written_strings.append(ProgramBinary.String(literal))

        self._fields.append(written_strings)

    def _parse_options(self):
        written_options = []
        for i in range(self._metadata.n_options):
            option_stmt = self.program._option_statements[i]
            pc = self.program._option_statements_pc[i]

            value = value_from_token(option_stmt.string_token)
            identifier = anonymous_identifier(value)
            variable = self._type_checker.read_variable(identifier)
            string_index = variable.index

            written_options.append(ProgramBinary.Option(string_index, pc))

        self._fields.append(written_options)

    def _parse_instructions(self):
        written_instructions = []
        for i in range(self._metadata.n_instructions):
            instruction = self.program.instructions[i]
            if isinstance(instruction, inst.LiteralInstruction):
                literal = instruction.literal
            else:
                literal = 0

            written_instructions.append(
                ProgramBinary.Instruction(instruction.op_code, literal))

        self._fields.append(written_instructions)
