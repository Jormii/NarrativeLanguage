from enum import Enum, auto


class VariableType(Enum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()


class Identifier:

    def __init__(self, name):
        self.name = name

    def copy(self):
        return Identifier(str(self.name))

    def __eq__(self, o):
        if not isinstance(o, Identifier):
            return False

        return self.name == o.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


class Value:

    def __init__(self, variable_type, literal):
        self.variable_type = variable_type
        self.literal = literal

    def copy(self):
        t = type(self.literal)
        return Value(self.variable_type, t(self.literal))

    def __repr__(self):
        return "({}) {}".format(self.variable_type.name, self.literal)

    @staticmethod
    def congruent(value_a, value_b):
        return value_a.variable_type == value_b.variable_type


class Variable:

    def __init__(self, identifier, value, index):
        self.identifier = identifier
        self.value = value
        self.index = index

    def __repr__(self):
        return "{} = {}".format(self.identifier, self.value)


class Variables:

    def __init__(self):
        self._in_order = []
        self._index_mapping = {}

    def defined(self, identifier):
        return identifier in self._index_mapping

    def define(self, identifier, value):
        index = len(self._in_order)
        variable = Variable(identifier, value, index)

        self._in_order.append(variable)
        self._index_mapping[identifier] = index

    def read(self, identifier):
        index = self._index_mapping[identifier]
        return self._in_order[index]

    def length(self):
        return len(self._in_order)
