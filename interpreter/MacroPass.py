import numbers
from LoteosMain import Loteos
from Enviroment import Environment
from LoxRuntimeError import LoxRuntimeError

from LoteosEnum import CommandType


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


class MacroPass:
    def __init__(self, list_of_local_varibales):
        self.macro_table = {}

    def macro_pass(self, statements):
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError:
            Loteos().runtime_error(LoxRuntimeError)

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


    def visit_pythonref(self, stmt ):
        """
        add the ref to the macro table
        :return:
        """
        self.macro_table[stmt.name] = self.list_of_local_varibales[stmt.name]

    def visit_assert(self, stmt):
        """
        assert that the execution of the command meets the provided consistency requirement
        :param stmt: command + consistency_level
        :return: None
        """
        # ToDo execute the command
        # ToDo observe the returned status
        # ToDo compare the status with the consistency_level
        print "assert"
        pass

    def visit_command(self, stmt):
        """
        Semantics of Loteos statements
        :param stmt: command + params
        :return: None
        """
        # execute the command
        if stmt.command_type == CommandType.GET_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.PUT_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.REMOVE_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.LOCK_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.UNLOCK_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.REGISTER_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.PUBLISH_COMMAND:
            stmt.accept(self)
        elif stmt.command_type == CommandType.SUBSCRIBE_COMMAND:
            stmt.accept(self)
        else:
            raise RuntimeError("Unsupported command")

    def visit_block(self, stmt):  # of type : Block
        self._execute_block(stmt.statements, Environment(self.globals))
        return None

    def visit_expression(self,  stmt):
        self._evaluate(stmt.expression)

    def visit_function(self, stmt): # stmt: Stmt.Function
        pass

    def visit_if(self, stmt):
        pass

    def visit_print(self,  stmt):
        value = self._evaluate(stmt.expression)
        print(_stringify(value))

    def visit_return(self, stmt):
        pass

    def visit_var(self, stmt):  # of type : Stmt.Var
        stmt.name.lexeme.accept(self)

    def visit_while(self, stmt):
        stmt.accept(self)

    def visit_assign(self, expr):  # of type Expr.Assign
        expr.value.accept()

    def visit_literal(self, expr):
        expr.accept(self)

    def visit_logical(self, expr):
        expr.accept(self)

    def visit_grouping(self, expr):
        expr.accept(self)

    def visit_unary(self, expr):
        expr.accept(self)

    def visit_variable(self, expr):  # of type : Expr.Variable
        expr.accept(self)

    def visit_binary(self, expr):
        expr.left.accept(self)
        expr.right.accept(self)

    def visit_call(self, expr):
        callee = self._evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            argument.accept(self)
