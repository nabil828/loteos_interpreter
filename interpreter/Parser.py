import grammar
# from Token import Token
from TokenType import TokenType
from LoteosEnum import CommandType
from LoteosEnum import ConsistencyType

# program     -> declaration* EOF ;
# 
# declaration -> funDecl
#             | varDecl
#             | statement
#             | lotoesCommand;
# 
# funDecl  -> "fun" function ;
# function -> IDENTIFIER "(" parameters? ")" block ;
# parameters -> IDENTIFIER ( "," IDENTIFIER )* ;

# lotoesCommand -> assert | command
# asser -> "assert" "(" command, consistency_level ")" ;
# command -> read | write | remove | lock | unlock
# read -> READ "(" primary ")" ;
# write -> WRITE "(" primary "," primary ")" ;
# remove -> REMOVE "(" primary ")" ;
# lock -> LOCK "(" primary ")" ;
# unlock -> UNLOCK "(" primary ")" ;

# consistency_level -> SC | EC | MC ;


# statement  -> exprStmt
#            | forStmt
#            | ifStmt
#            | printStmt
#            | returnStmt
#            | whileStmt
#            | block ;
# returnStmt -> "return" expression? ";" ;

#
# forStmt   -> "for" "(" ( varDecl | exprStmt | ";" )
#                       expression? ";"
#                       expression? ")" statement ;
# varDecl -> "var" IDENTIFIER ( "=" expression )? ";" ;

# whileStmt -> "while" "(" expression ")" statement ;
#
# ifStmt    -> "if" "(" expression ")" statement ( "else" statement )? ;
#
# block     -> "{" declaration* "}" ;
#
# exprStmt  -> expression ";" ;
# printStmt -> "print" expression "


# expression -> assignment ;
# assignment -> identifier "=" assignment
#            | logic_or ;
# logic_or   -> logic_and ( "or" logic_and )* ;
# logic_and  -> equality ( "and" equality )* ;

# equality       -> comparison ( ( "!=" | "==" ) comparison )* ;
# comparison     -> addition ( ( ">" | ">=" | "<" | "<=" ) addition )* ;
# addition       -> multiplication ( ( "-" | "+" ) multiplication )* ;
# multiplication -> unary ( ( "/" | "*" ) unary )* ;

# unary -> ( "!" | "-" ) unary | call ;
# call  -> primary ( "(" arguments? ")" )* ;
# arguments -> expression ( "," expression )* ;

#                | primary ;
# primary        -> NUMBER | STRING | "false" | "true" | "nil"
#                | "(" expression ")"  | IDENTIFIER ;

class ParseError(Exception):
    """Raise for an unexpected token in the parser."""


class Parser:

    def __init__(self, interpreter, token_list):

        self._interpreter = interpreter

        # The current head index in the token list
        self._current = 0

        self.token_list = token_list

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
        statement -> exprStmt
          | printStmt
          | block ;"""
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
        else:
            return self._expression_statement()

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
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return grammar.Var(name, initializer)

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
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, grammar.Variable):
                name = expr.name
                return grammar.Assign(name, value)
            self.error(equals, "Invalid assignment target.")

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

    def _declaration(self, _str=""):
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
            elif self._match(TokenType.ASSERT):
                return self._assert()
            elif self._match(TokenType.READ):
                return self._read_command(_str)
            elif self._match(TokenType.WRITE):
                return self._write_command(_str)
            elif self._match(TokenType.REMOVE):
                return self._remove_command(_str)
            elif self._match(TokenType.LOCK):
                return self._lock_command()
            elif self._match(TokenType.UNLOCK):
                return self._unlock_command()
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
        self._consume(TokenType.SEMICOLON, "Expect ';' after assert statement.");
        return grammar.Assert(_command, _consistency_level)

    def _read_command(self, _str=""):
        """
        Matches based on the rule
        # read -> READ "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after read.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after read.")
        if _str != "coming_from_assert":
            self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.");
        return grammar.Command(CommandType.GET_COMMAND, _key)

    def _write_command(self, _str=""):
        """
        Matches based on the rule
        # write -> WRITE "(" primary "," primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after write.")
        _key = self._primary()
        self._consume(TokenType.COMMA, "Except ',' after command's key.")
        _value = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after command's key.")
        if _str != "coming_from_assert":
            self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.");
        return grammar.Command(CommandType.PUT_COMMAND, [_key, _value])

    def _remove_command(self, _str=""):
        """
        Matches based on the rule
        # remove -> REMOVE "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after remove.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after remove.")
        if _str != "coming_from_assert":
            self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.");
        return grammar.Command(CommandType.REMOVE_COMMAND, _key)

    def _lock_command(self):
        """
        Matches based on the rule
        # lock -> LOCK "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after lock.")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after lock.")
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.");
        return grammar.Command(CommandType.LOCK_COMMAND, _key)

    def _unlock_command(self):
        """
        Matches based on the rule
        # unlock -> UNLOCK "(" primary ")" ;
        """
        self._consume(TokenType.LEFT_PAREN, "Except '(' after unlock .")
        _key = self._primary()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after unlock.")
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.");
        return grammar.Command(CommandType.UNLOCK_COMMAND, _key)

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
        if self._match(TokenType.FALSE):
            return grammar.Literal(False)
        elif self._match(TokenType.TRUE):
            return grammar.Literal(True)
        elif self._match(TokenType.NIL):
            return grammar.Literal(None)

        elif self._match(TokenType.NUMBER, TokenType.STRING):
            return grammar.Literal(self._previous().literal)

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
