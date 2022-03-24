class StringTraversal:

    EOS = -1

    def __init__(self, string):
        self.string = string

        self._pos = 0

    def current_index(self):
        return self._pos

    def at_end(self):
        return self._pos >= len(self.string)

    def get(self):
        if self.at_end():
            return StringTraversal.EOS

        return self.string[self._pos]

    def peek(self):
        self._pos += 1
        c = self.get()
        self._pos -= 1

        return c

    def get_and_advance(self):
        if self.at_end():
            return StringTraversal.EOS

        self._pos += 1
        return self.string[self._pos - 1]

    def match_and_if_so_advance(self, char):
        if self.at_end():
            return False

        c = self.get()
        match = c == char
        if match:
            self.get_and_advance()

        return match
