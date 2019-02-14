import Scanner
from interpreter.LoteosEnum import CommandType
from interpreter.LoteosEnum import ConsistencyType
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


class Call(Expr):
    def __init__(self, callee, paren, arguments):
        assert isinstance(callee, Expr)
        assert isinstance(paren, Scanner.Token)
        # assert isinstance(arguments, Expr)

        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call(self)


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


class PythonRef(Expr):
    def __init__(self, name):
        # assert isinstance(name, Scanner.Token)

        self.name = name

    def accept(self, visitor):
        return visitor.visit_pythonref(self)


class Assign(Expr):
    def __init__(self, name, value, assign_type):
        # assert isinstance(name, Scanner.Token)
        assert isinstance(value, Expr)
        assert isinstance(assign_type, object)

        self.name = name
        self.value = value
        self.assign_type = assign_type

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
from interpreter.LoteosEnum import CommandType
from interpreter.LoteosEnum import ConsistencyType
class Stmt:
    pass


class Function(Stmt):
    def __init__(self, name, params, body):
        assert isinstance(name, Scanner.Token)
        assert isinstance(params, Scanner.Token)
        assert isinstance(body, Stmt)

        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function(self)


class Var(Stmt):
    def __init__(self, name, initializer):
        assert isinstance(name, Scanner.Token)
        # assert isinstance(initializer, Expr)

        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var(self)


class While(Stmt):
    def __init__(self, condition, body):
        assert isinstance(condition, Expr)
        assert isinstance(body, Stmt)

        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while(self)


class Return(Stmt):
    def __init__(self, keyword, value):
        assert isinstance(keyword, Scanner.Token)
        assert isinstance(value, Expr)

        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return(self)


class Print(Stmt):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print(self)


class Expression(Stmt):
    def __init__(self, expression):
        assert isinstance(expression, Expr)

        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression(self)


class Block(Stmt):
    def __init__(self, statements):
        # assert isinstance(statements, Stmt)

        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block(self)


class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        assert isinstance(condition, Expr)
        # assert isinstance(then_branch, Stmt)
        assert isinstance(else_branch, Stmt)

        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if(self)

import Scanner
from interpreter.LoteosEnum import CommandType
from interpreter.LoteosEnum import ConsistencyType
class LoteosDirective:
    pass


class LoteosStmt(LoteosDirective):
    def __init__(self, stmt):
        assert isinstance(stmt, LoteosDirective)

        self.stmt = stmt

    def accept(self, visitor):
        return visitor.visit_loteosstmt(self)


class Assert(LoteosDirective):
    def __init__(self, cmd, consistency_type):
        assert isinstance(cmd, Command)
        assert isinstance(consistency_type, ConsistencyType)

        self.cmd = cmd
        self.consistency_type = consistency_type

    def accept(self, visitor):
        return visitor.visit_assert(self)


class Command(LoteosDirective):
    def __init__(self, command_type, params):
        # assert isinstance(command_type, CommandType)
        # assert isinstance(params, Scanner.Token)

        self.command_type = command_type
        self.params = params

    def accept(self, visitor):
        return visitor.visit_command(self)

