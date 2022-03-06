from NarrativeLanguage import scanner, parser
from NarrativeLanguage.formatter import FORMATTER
from NarrativeLanguage.interpreter import INTERPRETER

from VirtualMachine.type_checker import TypeChecker
from VirtualMachine.program import Program
from VirtualMachine.program_execution import ProgramExecution

DEBUG = False


def main():
    path = "./example3.txt"
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
                print(INTERPRETER.visit(stmt))

            print(100 * "-")

        # Check types and resolve macros
        checker = TypeChecker(parse.statements)
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


if __name__ == "__main__":
    main()
