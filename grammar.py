import Scanner


class Expr:
    pass


class Binary(Expr):
    def __init__(self, left, operator, right):
        assert isinstance(left, Expr)
        assert isinstance(operator, Scanner.Token)
        assert isinstance(right, Expr)

        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary(self)


class Chain(Expr):
    def __init__(self, left, right):
        assert isinstance(left, Expr)
        assert isinstance(right, Expr)

        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_chain(self)


class Unary(Expr):
    def __init__(self, operator, right):
        assert isinstance(operator, Scanner.Token)
        assert isinstance(right, Expr)

        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary(self)


class Literal(Expr):
    def __init__(self, value):
        assert isinstance(value, object)

        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)


class Variable(Expr):
    def __init__(self, name):
        assert isinstance(name, Scanner.Token)

        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable(self)


class Grouping(Expr):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping(self)

import Scanner


class Stmt:
    pass


class Print(Stmt):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print(self)


class Var(Stmt):
    def __init__(self, name, initializer):
        assert isinstance(name, Scanner.Token)
        assert isinstance(initializer, Expr)

        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var(self)


class Expression(Stmt):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression(self)

