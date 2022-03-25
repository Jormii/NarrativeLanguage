import os

from NarrativeLanguage.variables import VariableScope

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
            options_count = len(self.program.options)
            integers_count = self.program.offsets.count_integers(
                self.program.solver)
            instructions_offset = self.program.offsets.offset
            stack_size = self.program.max_stack_size

            header = types.HeaderField(
                options_count, integers_count, instructions_offset, stack_size)
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

    @staticmethod
    def write_global_vars_to_file(global_vars, path):
        with open(path, "wb") as fd:
            for i, variable in enumerate(global_vars.variables.values()):
                assert i == variable.index

                fd.write(types.IntField(variable.value.literal).to_bytes())
