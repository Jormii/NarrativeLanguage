from NarrativeLanguage import scanner, parser
from NarrativeLanguage.formatter import FORMATTER
from NarrativeLanguage.interpreter import INTERPRETER


def main():
    path = "./example.txt"
    with open(path, "r") as f:
        source_code = f.read()

        # TODO: Remove
        source_code = "10 * ((1.2 - 2 + 3) / 5)"

        scan = scanner.Scanner(source_code)
        scan.scan()
        for token in scan.tokens:
            print(token)

        print(100 * "-")

        parse = parser.Parser(scan.tokens)
        parse.parse()
        for stmt in parse.statements:
            print(FORMATTER.visit(stmt))


if __name__ == "__main__":
    main()
