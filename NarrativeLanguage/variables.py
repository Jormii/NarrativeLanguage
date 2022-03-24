from enum import Enum, auto


class Identifier:

    def __init__(self, name):
        self.name = name

    def __eq__(self, o):
        if not isinstance(o, Identifier):
            return False

        return self.name == o.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


class ValueType:

    def __init__(self, name):
        self.name = name

    def __eq__(self, o):
        if not isinstance(o, ValueType):
            return False

        return self.name == o.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return repr(self.name)


INT_TYPE = ValueType("INT")
FLOAT_TYPE = ValueType("FLOAT")
STRING_TYPE = ValueType("STRING")
STRING_PTR_TYPE = ValueType("STRING*")
SCENE_IDENTIFIER_TYPE = ValueType("SCENE")


class Value:

    def __init__(self, value_type, literal):
        self.value_type = value_type
        self.literal = literal

    def __repr__(self):
        return "({} {})".format(self.value_type, self.literal)


class VariableScope(Enum):
    GLOBAL_DEFINE = auto()
    GLOBAL_DECLARE = auto()
    STORE = auto()
    TEMPORAL = auto()


class Variable:

    def __init__(self, scope, identifier, value):
        self.scope = scope
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return "_{}_ {} = {}".format(
            self.scope.name, self.identifier, self.value)


class Variables:

    def __init__(self):
        self.variables = {}

    def is_defined(self, identifier):
        return identifier in self.variables

    def define(self, scope, identifier, value):
        variable = Variable(scope, identifier, value)
        self.variables[identifier] = variable

    def read(self, identifier):
        return self.variables[identifier]
