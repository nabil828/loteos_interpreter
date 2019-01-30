import grammar
# from Token import Token
from TokenType import TokenType

# program     -> declaration* EOF ;
# 
# declaration -> varDecl
#             | statement ;
# 


# statement -> exprStmt
#           | forStmt
#           | ifStmt
#           | printStmt
#           | whileStmt
#           | block ;
#
# forStmt   -> "for" "(" ( varDecl | exprStmt | ";" )
#                       expression? ";"
#                       expression? ")" statement ;
#
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
# unary          -> ( "!" | "-" ) unary
#                | primary ;
# primary        -> NUMBER | STRING | "false" | "true" | "nil"
#                | "(" expression ")" ;

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
        else:
            return self._expression_statement()

    def _if_statement(self):
        self._consume(TokenType.LEFT_PAREN, "Except '(' after if.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Except ')' after if conditon.")

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
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self.expression()
        self._consume(TokenType.SEMICOLON, "Except ';' after loop condition.")

        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Excpet ';' after for caluses.")

        body = self.statement()

        if increment is not None:
            body = grammar.Block([body, grammar.Expr(increment)])

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

    def var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.");
        return grammar.Var(name, initializer)

    def _expression_statement(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.");
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

    def _declaration(self):
        """
        Matches based on the rule:
        declaration -> varDecl
            | statement ;
        """
        try:
            if self._match(TokenType.VAR):
                return self.var_declaration()
            return self._statement()
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
        """Matches based on the rule:
        unary -> ( ! | - ) unary
               | primary"""
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return grammar.Unary(operator, right)

        return self._primary()

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
