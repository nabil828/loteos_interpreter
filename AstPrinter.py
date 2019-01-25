#! /usr/local/bin/python3

import grammar
# import scanner
from TokenType import TokenType
from Token import Token


class AstPrinter:
    def print_ast(self, expr):
        return expr.accept(self)

    def visit_chain(self, expr):
        return self.parenthesize("chain", expr.left, expr.right)

    def visit_binary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal(self, expr):
        return str(expr.value)

    def visit_unary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        string = "(" + name

        for expr in exprs:
            string += " "
            string += expr.accept(self)

        string += ")"

        return string


if __name__ == "__main__":
    expression = grammar.Binary(
        grammar.Unary(
            Token(TokenType.MINUS, "-", None, 1),
            grammar.Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        grammar.Grouping(
            grammar.Literal(45.67)))
    print(AstPrinter().print_ast(expression))
