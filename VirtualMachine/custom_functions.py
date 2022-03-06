from VirtualMachine.variables import VariableType as T
from VirtualMachine.function import Function, FunctionPrototypes


class MultiplyFunc(Function):

    def __init__(self):
        super().__init__("multiplicar", [T.INT, T.INT])

    def call(self, args):
        print("{} x {} = {}".format(args[0], args[1], args[0]*args[1]))
        return 1


prototypes = FunctionPrototypes()
prototypes.define(MultiplyFunc())
