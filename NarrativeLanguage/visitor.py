class Visitor:

    def __init__(self):
        self._cb = {}

    def submit(self, type, callback):
        self._cb[type] = callback

        return self

    def visit(self, obj):
        t = type(obj)
        cb = self._cb.get(t)
        assert cb is not None, \
            "Can't visit expression of type {}".format(t)

        return cb(obj)
