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
        return visitor.visitUnary(self)


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
        return visitor.visitChain(self)


class Grouping(Expr):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visitGrouping(self)


class Stmt:
    pass


class Print(Stmt):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class Expression(Stmt):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

