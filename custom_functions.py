import NarrativeLanguage.function as funcs
import NarrativeLanguage.variables as variables


class CustomAdd(funcs.Function):

    def __init__(self):
        super().__init__(
            "custom_add",
            variables.INT_TYPE,
            [variables.INT_TYPE, variables.INT_TYPE]
        )


class Name(funcs.Function):

    def __init__(self):
        super().__init__("name", variables.STRING_PTR_TYPE, [])


class Color(funcs.Function):

    def __init__(self):
        super().__init__("color", variables.STRING_PTR_TYPE,
                         [variables.INT_TYPE, variables.INT_TYPE, variables.INT_TYPE])


prototypes = funcs.FunctionPrototypes()
prototypes.define(CustomAdd())
prototypes.define(Name())
prototypes.define(Color())
