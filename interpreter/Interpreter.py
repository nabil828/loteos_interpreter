import numbers
from TokenType import TokenType
# from LoteosMain import Loteos
from Enviroment import Environment
from LoxRuntimeError import LoxRuntimeError
from LoxCallable import LoxCallable
from LoxFunction import LoxFunction
from Return import Return
from LoteosEnum import CommandType
import Command
import pickle

import json
from thin_client.LoteosThinClientSupport import QueueObj, outgoing_requests_q, response_q


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
    registered_id = None

    def __init__(self, locals_, globals_):
        self.globals = Environment()
        self.current_environment = self.globals
        # for python variables
        self.py_locals = locals_
        self.py_globals = globals_

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
            # Loteos().runtime_error(LoxRuntimeError)
            print(LoxRuntimeError.message, "\n[line ", LoxRuntimeError.token.line, "]")

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

    def visit_assert(self, stmt):
        """
        assert that the execution of the command meets the provided consistency requirement
        :param stmt: command + consistency_level
        :return: None
        """
        # ToDo execute the command
        # ToDo observe the returned status
        # ToDo compare the status with the consistency_level
        print "asssert"
        pass

    def visit_loteosstmt(self, loteos_directive):
        self._evaluate(loteos_directive.stmt)

    def visit_command(self, loteos_directive):
        """
        Semantics of Loteos statements
        :param loteos_directive: command + params
        :return: None
        """
        # execute the command
        if loteos_directive.command_type == CommandType.GET_COMMAND:
            # print "get------"
            outgoing_requests_q.put(QueueObj(Command.GET, loteos_directive.params[0].value, ""))
            response_obj = response_q.get()
            # Environment stuff
            return response_obj.value
        elif loteos_directive.command_type == CommandType.PUT_COMMAND:
            # print "put------"

            # if loteos_directive.params[0].name.name.lexeme in self.macro_table:
            #     python_variable = loteos_directive.params[0].name.name.lexeme
            #     value_ = self.find(python_variable)  # ToDo: for now strings, later serialize it
            # else:
            #     value_ = loteos_directive.params[1].value
            value_ = self._execute(loteos_directive.params[1])
            outgoing_requests_q.put(QueueObj(Command.PUT, loteos_directive.params[0].value, value_))
            response_obj = response_q.get()
            # print "put responsae" + Response.print_response(response_obj.response)
            # if response_obj.value == Response.SUCCESS:  # Mainly for the GET commands
            #     return response_obj.response_value
            # else:
            #     return None
        elif loteos_directive.command_type == CommandType.REMOVE_COMMAND:
            print "remove------"
            outgoing_requests_q.put(QueueObj(Command.REMOVE, loteos_directive.params[0].value, ""))
            response_obj = response_q.get()
        elif loteos_directive.command_type == CommandType.LOCK_COMMAND:
            print "lock------"
            outgoing_requests_q.put(QueueObj(Command.LOCK, loteos_directive.params[0].value, ""))
            response_obj = response_q.get()
        elif loteos_directive.command_type == CommandType.UNLOCK_COMMAND:
            print "unlock------"
            outgoing_requests_q.put(QueueObj(Command.UNLOCK, loteos_directive.params[0].value, ""))
            response_obj = response_q.get()

        elif loteos_directive.command_type == CommandType.REGISTER_COMMAND:
            # print "register------"
            Interpreter.registered_id = loteos_directive.params[0].value
            # Todo: how to enumerate string_id?
            outgoing_requests_q.put(QueueObj(Command.REGISTER, Interpreter.registered_id, ""))
            response_obj = response_q.get()
            print response_obj.response
        elif loteos_directive.command_type == CommandType.PUBLISH_COMMAND:
            # print "publish------"
            # we got a key and a msg
            # CONSTRUCT MSG IN VALUE
            # get it from the table
            # if loteos_directive.params[0].name.name.lexeme in self.macro_table:
            #     python_variable = loteos_directive.params[0].name.name.lexeme
            #     t_ = self.find(python_variable)
            #
            #     # t_[2] = t_[2].toJSON()
            #     # to_be_sent = json.dumps(t_)
            #     to_be_sent = pickle.dumps(t_)
            # else:
            #     to_be_sent = json.dumps(loteos_directive.params[0].name.name.lexeme)
            to_be_sent = self._execute(loteos_directive.params[0])
            to_be_sent = pickle.dumps(to_be_sent)
            obj = QueueObj(Command.PUBLISH, Interpreter.registered_id, to_be_sent)
            outgoing_requests_q.put(obj)
            l = outgoing_requests_q.qsize()
            response_obj = response_q.get()
            print response_obj.response
        elif loteos_directive.command_type == CommandType.SUBSCRIBE_COMMAND:
            # print "subscribe------"
            # we got the channel name (key)
            outgoing_requests_q.put(QueueObj(Command.SUBSCRIBE, Interpreter.registered_id, loteos_directive.params[0].value))
            response_obj = response_q.get()
        else:
            raise RuntimeError("Unsupported command")
        # observe the returned status
        # ToDo

    def find(self, _string):
        for k, v in list(self.py_locals.iteritems()):
            if k == _string:
                return v
        for k, v in list(self.py_globals.iteritems()):
            if k == _string:
                return v
                # ToDo Serialize
                # result = []
                # for item in v:
                #     result.append(json.dumps(item, default=lambda o: o.__dict__,
                #                       sort_keys=True, indent=4))
                # return result

    def visit_block(self, stmt):  # of type : Block
        self._execute_block(stmt.statements, Environment(self.globals))
        return None

    def visit_expression(self,  stmt):
        self._evaluate(stmt.expression)

    def visit_function(self, stmt): # stmt: Stmt.Function
        function_ = LoxFunction(stmt, self.current_environment)
        self.current_environment.define(stmt.name.lexeme, function_)
        return None

    def visit_if(self, stmt):
        if _is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)
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
        if stmt.initializer is not None:  # ??
            value = self._evaluate(stmt.initializer)

        self.globals.define(stmt.name.lexeme, value)
        return None

    def visit_while(self, stmt):
        while _is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

        return None

    def visit_assign(self, expr):  # of type Expr.Assign
        value = self._evaluate(expr.value)
        if expr.assign_type == "loteos_var":
            self.globals.assign(expr.name, value)
        else:  # python ref
            assert expr.assign_type == "python_var"
            if str(value) == "":
                value = "\"\""
            exec ('global ' + str(expr.name) + '; ' + str(expr.name) + ' =' + "\"" + str(value) + "\"", self.py_globals, self.py_locals)
            # tmp = self.py_globals[expr.name.lexeme]
            # if self.py_globals[expr.name.lexeme] is not None:
            #     self.py_globals[expr.name.lexeme] = str(value)
            # elif self.py_locals[expr.name.lexeme] is not None:
            #     self.py_locals[expr.name.lexeme] = str(value)
            # else:
            #     raise RuntimeError

        return value

    def visit_pythonref(self, expr):
        return self.find(expr.name)

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