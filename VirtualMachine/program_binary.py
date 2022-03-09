import os


import VirtualMachine.types as types
import VirtualMachine.instruction as inst
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
            out_f.write(types.OffsetField(
                self.program.options_offset).to_bytes())
            out_f.write(types.OffsetField(
                self.program.instructions_offset).to_bytes())

            for identifier in self.program.offsets.keys():
                variable = self.program.solver.read(identifier)
                cb = types.VALUE_TYPE_CALLBACKS[variable.value.value_type]
                field = cb(variable)
                out_f.write(field.to_bytes())

            for string_offset, pc in self.program._option_statements_data:
                field = types.OptionField(string_offset, pc)
                out_f.write(field.to_bytes())

            for instruction in self.program.instructions:
                op_code = instruction.op_code
                if isinstance(instruction, inst.NoLiteralInstruction):
                    literal = 0
                else:
                    literal = instruction.literal

                # Python enums start at 1
                field = types.InstructionField(op_code.value - 1, literal)
                out_f.write(field.to_bytes())

        print("{}: {}".format(path, os.path.getsize(path)))
