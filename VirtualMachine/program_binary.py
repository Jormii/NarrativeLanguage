import os


import VirtualMachine.types as types
from VirtualMachine.program import Program


class ProgramBinary:

    def __init__(self, program: Program):
        self.program = program

    def write_to_file(self, path):
        head, tail = os.path.split(path)

        assert len(tail) != 0, "Path doesn't describe a file"
        if not os.path.exists(head):
            os.makedirs(head)

        with open(path, "wb") as out_f:
            # Header
            instruction_offset = self.program.offsets.offset
            options_counter = len(self.program.options)
            header = types.HeaderField(instruction_offset, options_counter)
            out_f.write(header.to_bytes())

            # Options
            for option in self.program.options:
                string_pc = option.string_pc
                instructions_pc = option.pc
                option_field = types.OptionField(string_pc, instructions_pc)
                out_f.write(option_field.to_bytes())

            # Variables
            for identifier in self.program.offsets.variables_offset.keys():
                variable = self.program.solver.read(identifier)
                cb = types.VALUE_TYPE_CALLBACKS[variable.value.value_type]
                variable_field = cb(variable)
                out_f.write(variable_field.to_bytes())

            # Instructions
            for instruction in self.program.instructions:
                op_code = instruction.op_code.value - 1  # Enums start at 1
                literal = instruction.get_literal()
                inst_field = types.InstructionField(op_code, literal)
                out_f.write(inst_field.to_bytes())

        print("{}: {}".format(path, os.path.getsize(path)))
