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


class Load(funcs.Function):

    def __init__(self):
        super().__init__("load", variables.INT_TYPE,
                         [variables.SCENE_IDENTIFIER_TYPE])


class RandomScene(funcs.Function):

    def __init__(self):
        super().__init__("random_scene", variables.SCENE_IDENTIFIER_TYPE, [])


prototypes = funcs.FunctionPrototypes()
prototypes.define(CustomAdd())
prototypes.define(Name())
prototypes.define(Load())
prototypes.define(RandomScene())
