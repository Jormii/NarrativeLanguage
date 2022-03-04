from NarrativeLanguage import scanner, parser
from NarrativeLanguage.formatter import FORMATTER
from NarrativeLanguage.interpreter import INTERPRETER

from VirtualMachine.type_checker import TypeChecker

DEBUG = False


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
                print(INTERPRETER.visit(stmt))

        # Check types and resolve macros
        checker = TypeChecker(parse.statements)
        checker.check()


if __name__ == "__main__":
    main()
