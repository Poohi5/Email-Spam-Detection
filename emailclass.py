import hashlib
class Email:
    def __init__(self, word, _class):
        self.word = word
        self._class = _class

    def __eq__(self, other):
        return self.word == other.word and self._class == other._class

    def __hash__(self):
        return hash((self.word, self._class))
