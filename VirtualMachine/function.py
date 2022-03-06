class Function:

    def __init__(self, name, params_types):
        self.name = name
        self.params_types = params_types

    def call(self, args) -> int:
        raise NotImplementedError()

    def __eq__(self, o):
        if not isinstance(o, Function):
            return False

        return self.name == o.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        args_names = []
        for arg_type in self.params_types:
            args_names.append(arg_type.name)

        return "{}({})".format(self.name, ", ".join(args_names))


class FunctionPrototypes:

    def __init__(self):
        self.functions = {}

    def defined(self, identifier):
        return identifier.name in self.functions

    def define(self, function):
        self.functions[function.name] = function
        return self

    def get(self, identifier):
        return self.functions[identifier.name]
