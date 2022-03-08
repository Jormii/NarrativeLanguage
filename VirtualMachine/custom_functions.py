import NarrativeLanguage.variables as variables
from NarrativeLanguage.function import Function, FunctionPrototypes


class IntMultiply(Function):

    def __init__(self):
        super().__init__(
            "multiplicar",
            variables.INT_TYPE,
            [variables.INT_TYPE, variables.INT_TYPE]
        )


to_define = [IntMultiply()]
prototypes = FunctionPrototypes()
for f in to_define:
    assert not prototypes.is_defined(f.identifier), \
        "Function with name '{}' already defined".format(f.identifier)

    prototypes.define(f)
