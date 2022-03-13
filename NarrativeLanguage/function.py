import NarrativeLanguage.variables as variables


class Function:

    def __init__(self, name, return_type, params_types):
        self.identifier = variables.Identifier(name)
        self.return_type = return_type
        self.params_types = params_types

        # TODO: Remove this later
        assert self.return_type != variables.FLOAT_TYPE, \
            "Floats aren't allowed for now"

    def compatible_args(self, values):
        if len(self.params_types) != len(values):
            return False

        for expected_type, value in zip(self.params_types, values):
            if expected_type != value.value_type:
                return False

        return True

    def __eq__(self, o):
        if not isinstance(o, Function):
            return False

        return self.identifier == o.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        args_names = []
        for arg_type in self.params_types:
            args_names.append(repr(arg_type))

        return "{}({}) -> {}".format(
            self.identifier, ", ".join(args_names), self.return_type)


class FunctionPrototypes:

    def __init__(self):
        self.functions = {}

    def is_defined(self, identifier):
        return identifier in self.functions

    def define(self, function):
        self.functions[function.identifier] = function
        return self

    def get(self, identifier):
        return self.functions[identifier]
