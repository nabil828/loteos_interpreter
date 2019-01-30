import numbers
from TokenType import TokenType
import Lox
from Enviroment import Environment
from LoxRuntimeError import LoxRuntimeError
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from Return import Return


def _stringify(obj):
    if obj is None:
        return "nil"
    else:
        return str(obj)


def _is_truthy(obj):
    """Nil and false are false, everything else is true."""
    if obj is None:
        return False
    elif isinstance(obj, bool):
        return bool(obj)
    else:
        return True


def _is_equal(left, right):
    if left is None:
        if right is None:
            return True
        else:
            return False
    else:
        return left == right


def _concat_or_add(operator, left, right):
    if isinstance(left, numbers.Number) and isinstance(right, numbers.Number):
        return float(left) + float(right)
    elif isinstance(left, str) and isinstance(right, str):
        return left + right
    else:
        raise LoxRuntimeError(operator, "Operands must be two numbers or two strings.")


def _check_number_operand(operator, operand):
    if isinstance(operand, numbers.Number):
        return

    raise LoxRuntimeError(operator, "Operand must be a number.")


def _check_number_operands(operator, left, right):
    if isinstance(left, numbers.Number) and isinstance(right, numbers.Number):
        return
    raise LoxRuntimeError(operator, "Operands must be numbers.")


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.current_environment = self.globals

        # Anonymous objects in Python
        # anon = type('',(object,),{})()
        # http://www.hydrogen18.com/blog/python-anonymous-objects.html
        # self.globals.define("clock", type('AnonymousClass', (LoxCallable,),
        #                                   {'arity': lambda self: 0,
        #                                    'call': lambda self, interpreter, arguments: time.clock()})())

    def interpret(self, statements):
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError:
            Lox.Lox().runtime_error(LoxRuntimeError)

    def _evaluate(self, expr):
        return expr.accept(self)

    def _execute(self, stmt):
        return stmt.accept(self)

    def _execute_block(self, statements, environment):
        previous = self.globals
        try:
            self.globals = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.globals = previous

    def visit_block(self, stmt): # of type : Block
        self._execute_block(stmt.statements, Environment(self.globals))
        return None

    def visit_expression(self,  stmt):
        self._evaluate(stmt.expression)

    def visit_function(self, stmt): #stmt: Stmt.Function
        function_ = LoxFunction(stmt, self.current_environment)
        self.current_environment.define(stmt.name.lexeme, function_)
        return None

    def visit_if(self, stmt):
        if _is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(self._evaluate(stmt.else_branch))
        return None

    def visit_print(self,  stmt):
        value = self._evaluate(stmt.expression)
        print(_stringify(value))

    def visit_return(self, stmt):
        value = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)
        raise Return(value)

    def visit_var(self, stmt):  # of type : Stmt.Var
        value = None
        if stmt.initializer is not None:  #??
            value = self._evaluate(stmt.initializer)

        self.globals.define(stmt.name.lexeme, value)
        return None

    def visit_while(self, stmt):
        while _is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

        return None

    def visit_assign(self, expr):  # of type Expr.Assign
        value = self._evaluate(expr.value)

        self.globals.assign(expr.name, value)
        return value

    def visit_literal(self, expr):
        return expr.value

    def visit_logical(self, expr):
        """short-circuits and return"""
        left = self._evaluate(expr.left)
        if expr.operator.type == TokenType.OR:  # or
            if _is_truthy(left):
                return left
        else:
            if not _is_truthy(left):
                return left

        return self._evaluate(expr.right)

    def visit_grouping(self, expr):
        return self._evaluate(expr.expression)

    def visit_unary(self, expr):
        right = self._evaluate(expr.right)

        op_type = expr.operator.token_type

        if op_type is TokenType.MINUS:
            _check_number_operand(expr.operator, right)
            return -float(right)
        elif op_type is TokenType.BANG :
            return _is_truthy(right)

        return None

    def visit_variable(self, expr):  # of type : Expr.Variable
        return self.globals.get(expr.name)

    def visit_binary(self, expr):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        op_type = expr.operator.token_type

        if op_type is TokenType.GREATER:
            _check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)

        elif op_type is TokenType.GREATER:
            _check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)

        elif op_type is TokenType.LESS:
            _check_number_operands(expr.operator, left, right)
            return float(left) < float(right)

        elif op_type is TokenType.LESS_EQUAL:
            _check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)

        elif op_type is TokenType.EQUAL_EQUAL:
            return _is_equal(left, right)

        elif op_type is TokenType.BANG_EQUAL:
            return not _is_equal(left, right)

        elif op_type is TokenType.MINUS:
            _check_number_operands(expr.operator, left, right)
            return float(left) - float(right)

        elif op_type is TokenType.PLUS:
            return _concat_or_add(expr.operator, left, right)

        elif op_type is TokenType.SLASH:
            _check_number_operands(expr.operator, left, right)
            return float(left) / float(right)

        elif op_type is TokenType.STAR:
            _check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        return None

    def visit_call(self, expr):
        callee = self._evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call function and classes.")

        function = callee
        if len(arguments) != function.arity():
            raise LoxRuntimeError(expr.paren, "Expected" + str(function.arity()) + "arguments but got {len(arguments)} .")

        return function.call(self, arguments)