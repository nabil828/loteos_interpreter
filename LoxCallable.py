class LoxCallable:  # interface
    def arity(self):
        pass

    def call(self, interpreter, arguments):
        pass