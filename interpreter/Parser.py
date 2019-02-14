import grammar
# from Token import Token
from TokenType import TokenType
from LoteosEnum import CommandType
from LoteosEnum import ConsistencyType

##################################################################################################
# Declarations: A program is a series of declarations, which are the statements                  #
# that bind new identifiers or any of the other statement types:                                 #
##################################################################################################
# program     -> declaration* EOF ;
# 
# declaration -> funDecl
#             | varDecl
#             | statement ;
# 
# funDecl  -> "fun" function ;
# varDecl -> "var" IDENTIFIER ( "=" expression | read )? ";" ;


##################################################################################################
# Statements: The remaining statement rules produce side effects, but do not introduce bindings: #
##################################################################################################
# statement  -> exprStmt
#            | forStmt
#            | ifStmt
#            | printStmt
#            | returnStmt
#            | whileStmt
#            | block
#            | lotoesCommandStmt
#            ;

# exprStmt  -> expression ";" ;
# forStmt   -> "for" "(" ( varDecl | exprStmt | ";" )
#                       expression? ";"
#                       expression? ")" statement ;
# ifStmt    -> "if" "(" expression ")" statement ( "else" statement )? ;
# printStmt -> "print" expression ";" ;
# returnStmt -> "return" expression? ";" ;
# whileStmt -> "while" "(" expression ")" statement ;
# block     -> "{" declaration* "}" ;


##################################################################################################
# Expressions: Expressions produce values.                                                       #
##################################################################################################
# expression -> assignment ;
# assignment -> python_ref | IDENTIFIER "=" assignment | read | logic_or ;
# logic_or   -> logic_and ( "or" logic_and )* ;
# logic_and  -> equality ( "and" equality )* ;
#
# equality       -> comparison ( ( "!=" | "==" ) comparison )* ;
# comparison     -> addition ( ( ">" | ">=" | "<" | "<=" ) addition )* ;
# addition       -> multiplication ( ( "-" | "+" ) multiplication )* ;
# multiplication -> unary ( ( "/" | "*" ) unary )* ;
#
# unary -> ( "!" | "-" ) unary | call ;
# call  -> primary ( "(" arguments? ")" )* ;
# primary        ->  NUMBER | STRING | "false" | "true" | "nil"
#                | "(" expression ")"  | python_ref | python_ref | IDENTIFIER ;
# python_ref     -> "@" IDENTIFIER


###################################################
# Utility Rules:  reused helper rules:            #
###################################################
# function -> IDENTIFIER "(" parameters? ")" block ;
# parameters -> IDENTIFIER ( "," IDENTIFIER )* ;
# arguments -> expression ( "," expression )* ;


###################################################
# Loteos related rules                            #
###################################################
# lotoesCommandStmt -> lotoesCommand ";" ;
# lotoesCommand -> assert | command
#
# assert -> "assert" "(" command, consistency_level ")" ;
# command -> read | write | remove | lock | unlock | register | subscribe | publish
#
# read -> READ "(" primary ")" ;
# write -> WRITE "(" primary "," expression")" ;
# remove -> REMOVE "(" primary ")" ;
# lock -> LOCK "(" primary ")" ;
# unlock -> UNLOCK "(" primary ")" ;
# register -> REGISTER "(" primary ")" ;
# subscribe -> SUBSCRIBE "(" primary ")" ;
# publish -> PUBLISH "(" primary ")" ;
#
# consistency_level -> SC | EC | MC ;




class ParseError(Exception):
    """Raise for an unexpected token in the parser."""


class Parser:
    def __init__(self, interpreter, token_list):
        self._interpreter = interpreter

        # The current head index in the token list
        self._current = 0

        self.token_list = token_list
        # self.macro_table = {}

    def parse(self):
        statements = []
        while not self._is_at_end():
            try:
                statements.append(self._declaration())
            except ParseError as error:
                return None
        return statements

    def _match(self, *token_types):
        """Looks ahead one token. If the next token matches one of the
        given ones, returns true and advances the head pointer."""
        for token in token_types:
            if self._check(token):
                self._advance()
                return True

        return False

    def _check(self, token_type):
        """Checks the next token for the given token type."""
        """Unlike match(), it doesn't consume the token, it only looks at it."""
        if self._is_at_end():
            return False

        return self._peek().token_type == token_type

    def _advance(self):
        """Advances the head pointer by one if not at the end.
        Always returns the previous token."""
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _is_at_end(self):
        """Returns True if the next token is an EOF."""
        return self._peek().token_type == TokenType.EOF

    def _peek(self):
        """Returns the token to be consumed next."""
        return self.token_list[self._current]

    def _previous(self):
        """Returns the previous token in the list."""
        return self.token_list[self._current - 1]

    def _statement(self):
        """Matches based on the rule:
        # statement  -> exprStmt
        #            | forStmt
        #            | ifStmt
        #            | printStmt
        #            | returnStmt
        #            | whileStmt
        #            | block
        #            | lotoesCommandStmt
        #            ;
        """
        if self._match(TokenType.PRINT):
            return self._print_statement()
        elif self._match(TokenType.LEFT_BRACE):
            return grammar.Block(self._block_statement())
        elif self._match(TokenType.IF):
            return self._if_statement()
        elif self._match(TokenType.WHILE):
            return self._while_statement()
        elif self._match(TokenType.FOR):
            return self._for_statement()
        elif self._match(TokenType.RETURN):
            return self._return_statement()
        elif self._match_loteos():
            return self._loteos_command_statement()
        else:
            return self._expression_statement()

    def _match_loteos(self):
        if self._check(TokenType.READ):
            return True
        elif self._check(TokenType.WRITE):
            return True
        elif self._check(TokenType.REMOVE):
            return True
        elif self._check(TokenType.PUBLISH):
            return True
        elif self._check(TokenType.SUBSCRIBE):
            return True
        elif self._check(TokenType.REGISTER):
            return True
        elif self._check(TokenType.LOCK):
            return True
        elif self._check(TokenType.UNLOCK):
            return True
        return False

    def _if_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Except '(' after if.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after if condition.")

        _the_branch = self._statement()
        _else_branch = None
        if self._match(TokenType.ELSE):
            _else_branch = self._statement()

        return grammar.If(condition, _the_branch, _else_branch)

    def _while_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Except '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Except ') after condition.")
        body = self._statement()

        return grammar.While(condition, body)

    def _for_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Except '(' after 'for'.")

        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Except ';' after loop condition.")

        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Excpet ';' after for caluses.")

        body = self._statement()

        if increment is not None:
            body = grammar.Block([body, increment])

        if condition is None:
            condition = grammar.Literal(True)

        body = grammar.While(condition, body)

        if initializer is not None:
            body = grammar.Block([initializer, body])

        return body

    def _print_statement(self):
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return grammar.Print(value)

    def _return_statement(self):
        keyword = self._previous()
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return grammar.Return(keyword, value)

    def _var_declaration(self):
        """
        Matches based on the rule:
        varDecl -> "var" IDENTIFIER ( "=" expression | read )? ";"
        :return:
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self._match(TokenType.EQUAL):
            if self._match(TokenType.READ):
                initializer = self._read_command()
            else:
                initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return grammar.Var(name, initializer)

    def _loteos_command_statement(self):
        command = self._loteos_command()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return grammar.LoteosStmt(command)

    def _loteos_command(self):
        if self._match(TokenType.READ):
            return self._read_command()
        elif self._match(TokenType.WRITE):
            return self._write_command()
        elif self._match(TokenType.REMOVE):
            return self._remove_command()
        elif self._match(TokenType.PUBLISH):
            return self._publish_command()
        elif self._match(TokenType.SUBSCRIBE):
            return self._subscribe_command()
        elif self._match(TokenType.REGISTER):
            return self._register_command()
        elif self._match(TokenType.LOCK):
            return self._lock_command()
        elif self._match(TokenType.UNLOCK):
            return self._unlock_command()

    def _expression_statement(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return grammar.Expression(expr)

    def _block_statement(self):
        statements = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Except '}' after block.")
        return statements

    def _assignment(self):
        """
        Matches
        assignment -> identifier "=" assignment | read
        :return:
        """
        expr = self._or()

        if self._match(TokenType.READ):
            return self._read_command()
        elif self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, grammar.PythonRef):
                name = expr.name
                return grammar.Assign(name, value, "python_var")
            elif isinstance(expr, grammar.Variable):
                name = expr.name
                return grammar.Assign(name, value, "loteos_var")
            else:
                self._error(self._current, "Invalid assignment target.")
        return expr

    def _or(self):
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = grammar.Logical(expr, operator, right)

        return expr

    def _and(self):
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = grammar.Logical(expr, operator, right)

        return expr

    def _expression(self):
        """
        Matches based on the rule:
        expression -> equality
        """
        expr = self._assignment()
        return expr

    def _function(self, kind) :
        """
              Matches based on the rule:
              # function -> IDENTIFIER "(" parameters? ")" block ;
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect '(' after " + kind + " name.")
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after " + kind + " name.")
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 8:
                    self._error(self._peek(), "Cannot have more than 8 parameters.")
                parameters.append(self._consume(TokenType.IDENTIFIER, "Except parameter name."))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after parameters.")

        self._consume(TokenType.LEFT_BRACE, "Expect '{{' before {} body.".format(kind))
        body = self._block_statement()
        return grammar.Function(name, parameters, body)

    def _declaration(self):
        """
        Matches based on the rule:
        # declaration -> funDecl
        #             | varDecl
        #             | statement ;
        """
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            elif self._match(TokenType.FUN):
                return self._function("function")
            else:
                return self._statement()
        except ParseError:
            self._synchronize()
            return None

    def _assert(self):
        """
        Matches based on the rule:
        assert -> "assert" "(" command, consistency_level ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after assert.")
        _command = self._declaration("coming_from_assert")
        self._consume(TokenType.COMMA, "Except ',' after command key.")
        _consistency_level = self._consistency_level()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after assert argument.")

        return grammar.Assert(_command, _consistency_level)

    def _read_command(self):
        """
        Matches based on the rule
        # read -> READ "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after read.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after read.")

        return grammar.Command(CommandType.GET_COMMAND, (_key,))  # have it in a tuble: immutable list

    def _write_command(self):
        """
        Matches based on the rule
        # write -> WRITE "(" primary "," expression | python_ref")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after write.")
        _key = self._primary()
        self._consume(TokenType.COMMA, "Except ',' after command's key.")
        if self._check(TokenType.AT):
            _value = self._python_ref()
        else:
            _value = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after command's key.")

        return grammar.Command(CommandType.PUT_COMMAND, (_key, _value))

    def _remove_command(self):
        """
        Matches based on the rule
        # remove -> REMOVE "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after remove.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after remove.")

        return grammar.Command(CommandType.REMOVE_COMMAND, (_key,))

    def _register_command(self):
        """
        Matches based on the rule
        # register -> REGISTER "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after remove.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after remove.")

        return grammar.Command(CommandType.REGISTER_COMMAND, (_key,))

    def _publish_command(self):
        """
        Matches based on the rule
        # publish -> PUBLISH "("  python_ref")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after remove.")
        _value = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after remove.")

        return grammar.Command(CommandType.PUBLISH_COMMAND, (_value,))

    def _python_ref(self):
        """
        # python_ref     -> "@" IDENTIFIER
        :param _str:
        :return:
        """
        self._consume(TokenType.AT, "Expect '@' after expression.")
        python_variable_name = self._primary()
        # self.macro_table[python_variable_name.name.lexeme] = ""

        return grammar.PythonRef(python_variable_name.name.lexeme)

    def _subscribe_command(self):
        """
        Matches based on the rule
        # subscribe -> SUBSCRIBE "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after remove.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after remove.")

        return grammar.Command(CommandType.SUBSCRIBE_COMMAND, (_key,))

    def _lock_command(self):
        """
        Matches based on the rule
        # lock -> LOCK "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after lock.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after lock.")

        return grammar.Command(CommandType.LOCK_COMMAND, (_key,))

    def _unlock_command(self):
        """
        Matches based on the rule
        # unlock -> UNLOCK "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after unlock .")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after unlock.")

        return grammar.Command(CommandType.UNLOCK_COMMAND, (_key,))

    def _consistency_level(self):
        """
        Matches based on the rule:
        # consistency_level -> SC | EC | MC
        """
        try:
            if self._match(TokenType.SC):
                return ConsistencyType.SC
            elif self._match(TokenType.EC):
                return ConsistencyType.EC
            elif self._match(TokenType.MC):
                return ConsistencyType.MC
            raise ParseError("Invalid consistency level")
        except ParseError:
            self._synchronize()
            return None

    def _equality(self):
        """Matches based on the rule:
        equality -> comparison ( ( != | == ) comparison)*"""
        expr = self._comparison()

        # An Equality expression can match either a comparison
        # or comparison ((!= | ==) comparison)*
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = grammar.Binary(expr, operator, right)

        return expr

    def _comparison(self):
        """Matches based on the rule:
        comparison -> term ( ( > | >= | < | <= ) term)*"""
        expr = self._term()

        while self._match(TokenType.GREATER,
                          TokenType.GREATER_EQUAL,
                          TokenType.LESS,
                          TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = grammar.Binary(expr, operator, right)

        return expr

    def _term(self):
        """Matches based on the rule:
        term -> factor ( ( - | + ) factor)*"""
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = grammar.Binary(expr, operator, right)

        return expr

    def _factor(self):
        """Matches based on the rule:
        factor -> unary ( ( / | * ) unary)*"""
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = grammar.Binary(expr, operator, right)

        return expr

    def _unary(self):
        """
        Matches based on the rule:
        unary -> ( "!" | "-" ) unary | call ;
        """
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return grammar.Unary(operator, right)

        return self._call()

    def _call(self):
        """
        Matches based on the rule:
        call  -> primary ( "(" arguments? ")" )* ;
        """
        expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            else:
                break
        return expr

    def _finish_call(self, callee):
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                if len(arguments) >= 8:
                    self._error(self._peek(), "Cannot have more than 8 arguments.")
                arguments.append(self._expression())
        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return grammar.Call(callee, paren, arguments)

    def _primary(self):
        """
        Matches:
        primary        -> python_ref | NUMBER | STRING | "false" | "true" | "nil" | "(" expression ")"  | python_ref | IDENTIFIER ;
        :return:
        """
        if self._match(TokenType.FALSE):
            return grammar.Literal(False)
        elif self._match(TokenType.TRUE):
            return grammar.Literal(True)
        elif self._match(TokenType.NIL):
            return grammar.Literal(None)
        elif self._match(TokenType.NUMBER, TokenType.STRING):
            return grammar.Literal(self._previous().literal)
        elif self._match(TokenType.AT):
            # self._consume(TokenType.AT, "Expect @ before python referen.ce")
            self._advance()
            return grammar.PythonRef(self._previous().lexeme)
        elif self._match(TokenType.IDENTIFIER):
            return grammar.Variable(self._previous())
        elif self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN,
                          "Expect ')' after expression.")
            return grammar.Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def _consume(self, token_type, msg):
        """Attempts to consume the next token if it is the given type."""
        if self._check(token_type):
            return self._advance()

        raise self._error(self._peek(), msg)

    def _error(self, token, msg):
        """Returns a ParseError and logs an error with the interpreter."""
        self._interpreter.parse_error(token, msg)
        return ParseError()

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            end_statement_tokens = [TokenType.CLASS,
                                    TokenType.FUN,
                                    TokenType.VAR,
                                    TokenType.FOR,
                                    TokenType.IF,
                                    TokenType.WHILE,
                                    TokenType.PRINT,
                                    TokenType.RETURN]

            if self._peek().token_type in end_statement_tokens:
                return

            self._advance()
