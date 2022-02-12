def error(line: int, message: str):
    report(line, None, message)


def report(line: int, where: str, message: str):
    print("[Line {}]: Error {}: {}", line, where, message)
