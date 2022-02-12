from NarrativeLanguage import scanner

def main():
    path = "./example.txt"
    with open(path, "r") as f:
        source_code = f.read()
        scan = scanner.Scanner(source_code)
        scan.scan()
        
        for token in scan.tokens:
            print(token)
    
if __name__ == "__main__":
    main()
        