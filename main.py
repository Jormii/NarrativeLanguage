from NarrativeLanguage import scanner, parser
from NarrativeLanguage.formatter import FORMATTER
from NarrativeLanguage.interpreter import INTERPRETER


def main():
    path = "./example.txt"
    with open(path, "r") as f:
        source_code = f.read()
        scan = scanner.Scanner(source_code)
        scan.scan()
        for token in scan.tokens:
            print(token)

        print(100 * "-")

        parse = parser.Parser(scan.tokens)
        parse.parse()
        for stmt in parse.statements:
            print("> {}".format(FORMATTER.visit(stmt)))
            print(INTERPRETER.visit(stmt))


if __name__ == "__main__":
    main()
