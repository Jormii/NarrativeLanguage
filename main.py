import os

from NarrativeLanguage import scanner, parser
from NarrativeLanguage.macro_substitution import replace_macros
from NarrativeLanguage.formatter import FORMATTER
from NarrativeLanguage.variable_solver import VariableSolver

from VirtualMachine.program import Program
from VirtualMachine.program_binary import ProgramBinary
from VirtualMachine.c_call_interface import create_interface
from VirtualMachine.custom_functions import prototypes

DEBUG = True


def main():
    path = "./example.txt"
    with open(path, "r") as f:
        source_code = f.read()
        source_code = replace_macros(source_code)

        # Scan tokens
        scan = scanner.Scanner(source_code)
        scan.scan()

        if DEBUG:
            for token in scan.tokens:
                print(token)
            print(100 * "-")

        # Parse tokens
        parse = parser.Parser(scan.tokens)
        parse.parse()

        if DEBUG:
            for stmt in parse.statements:
                print("> {}".format(FORMATTER.visit(stmt)))

            print(100 * "-")

        # Check types and resolve macros
        solver = VariableSolver(parse.statements, prototypes)
        solver.solve()

        # Create program
        program = Program(parse.statements, solver)
        program.transpile()

        if DEBUG:
            program.pretty_print()

        # Write to file
        base, _ = os.path.splitext(path)
        out_path = "{}.bin".format(base)
        binary = ProgramBinary(program)

        binary.write_to_file(out_path)
        create_interface(program)


if __name__ == "__main__":
    main()
