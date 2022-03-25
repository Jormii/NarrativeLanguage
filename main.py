from multiprogram import MultiProgram
from VirtualMachine.custom_functions import prototypes

DEBUG = True


def main():
    paths = [
        "./example.txt",
        "./example2.txt",
        "./example3.txt",
        "./example4.txt"
    ]

    mp = MultiProgram(paths, prototypes)
    mp.compile("./binaries")


if __name__ == "__main__":
    main()
