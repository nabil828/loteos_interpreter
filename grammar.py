import Scanner


class Expr:
    pass


class Unary(Expr):
    def __init__(self, operator, right):
        assert isinstance(operator, Scanner.Token)
        assert isinstance(right, Expr)

        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary(self)


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


class Literal(Expr):
    def __init__(self, value):
        assert isinstance(value, object)

        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)


class Chain(Expr):
    def __init__(self, left, right):
        assert isinstance(left, Expr)
        assert isinstance(right, Expr)

        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_chain(self)


class Variable(Expr):
    def __init__(self, name):
        assert isinstance(name, Scanner.Token)

        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable(self)


class Assign(Expr):
    def __init__(self, name, value):
        assert isinstance(name, Scanner.Token)
        assert isinstance(value, Expr)

        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign(self)


class Logical(Expr):
    def __init__(self, left, operator, right):
        assert isinstance(left, Expr)
        assert isinstance(operator, Scanner.Token)
        assert isinstance(right, Expr)

        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical(self)


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


class Block(Stmt):
    def __init__(self, statements):
        assert isinstance(statements, Stmt)

        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block(self)


class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        assert isinstance(condition, Expr)
        assert isinstance(then_branch, Stmt)
        if else_branch is not None:
            assert isinstance(else_branch, Stmt)

        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if(self)

