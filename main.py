import os
from NarrativeLanguage import scanner, parser
from NarrativeLanguage.formatter import FORMATTER

from VirtualMachine.type_checker import TypeChecker
from VirtualMachine.program import Program
from VirtualMachine.program_execution import ProgramExecution
from VirtualMachine.program_binary import ProgramBinary
from VirtualMachine.custom_functions import prototypes

DEBUG = True


def main():
    path = "./example.txt"
    with open(path, "r") as f:
        source_code = f.read()

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
        checker = TypeChecker(parse.statements, prototypes)
        checker.check()

        # Create program
        program = Program(parse.statements, checker)
        program.transpile()

        if DEBUG:
            program.pretty_print()
            print(100 * "-")

        # Execute
        execution = ProgramExecution(program)
        execution.execute()

        # Write to file
        base, _ = os.path.splitext(path)
        out_path = "{}.bin".format(base)
        binary = ProgramBinary(program)
        binary.write_to_file(out_path)


if __name__ == "__main__":
    main()
