from  LoxRuntimeError import LoxRuntimeError


class Environment:
    def __init__(self):  # None for global scope's environment
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):  # of type Token
        """get name in current scope or outer scope"""
        if name.lexeme in self.values.keys():
            return self.values.get(name.lexeme)

        raise LoxRuntimeError(name,  "Undefined variable " + name.lexeme + ".")

    def assign(self, name, value):  # name of type Token
        """The key difference between assignment and definition is that assignment is not allowed to
        create a new variable."""
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise LoxRuntimeError(name, "Undefined variable " + name.lexeme + ".")
