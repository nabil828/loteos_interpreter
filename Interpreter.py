import numbers
from TokenType import TokenType
import Lox


class LoxRuntimeError(Exception):
    """Raise when the Lox interpreter encounters a runtime error."""
    def __init__(self, token, message):
        self.message = message
        self.token = token


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
        pass

    def interpret(self, statements):
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as error:
            Lox.Lox().runtime_error(error)

    def _evaluate(self, expr):
        return expr.accept(self)

    def _execute(self, stmt):
        return stmt.accept(self)

    def visit_expression_stmt(self,  stmt):
        self._evaluate(stmt.expression)

    def visit_print_stmt(self,  stmt):
        value = self._evaluate(stmt.expression)
        print(_stringify(value))

    def visit_literal(self, expr):
        return expr.value

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