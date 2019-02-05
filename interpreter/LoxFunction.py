from grammar import Stmt
from Enviroment import Environment
from LoxCallable import LoxCallable

from Return import Return


class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure): # declaration: Stmt.Function, closure: Environment)
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):  #def call(self, interpreter: "Interpreter", arguments: List[object]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter._execute_block(self.declaration.body, environment)
        except Return as returnValue:
            return returnValue.value

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return "<function " + "self.declaration.name.lexeme" + " >"
