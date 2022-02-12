from NarrativeLanguage import scanner, parser
from NarrativeLanguage.formatter import format_expression


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
        expr = parse.parse()
        print(format_expression(expr))


if __name__ == "__main__":
    main()
