import sys
import os
import Scanner
from TokenType import TokenType
import Parser
import AstPrinter

class Lox:
    had_error = False  # class variable

    # def __init__(self):

    # static method
    def run_prompt(self):
        while True:
            x = raw_input("> ")
            self.run(x)

            # If we had an error, we should reset at new prompt
            self.had_error = False

    # static method
    def run(self, source):
        # scanning
        obj = Scanner.Scanner(source)
        tokens = obj.scan_tokens()

        for token in tokens:
            print token

        parser = Parser.Parser(self, tokens)
        expression = parser.parse()

        # Stop if there was a syntax error.
        if self.had_error:
            return
        print(AstPrinter.AstPrinter().print_ast(expression))

    def parse_error(self, token, msg):
        if token.token_type == TokenType.EOF:
            self.report(token.line, "at end", msg)
        else:
            self.report(token.line, " at '" + token.lexeme + "'", msg)

    # static method
    def scan_error(self, line, message):
        self.report(line, "", message)

    # static method
    def report(self, line, where, message):
        print "[line " + line + "] Error" + where + ": " + message
        self.had_error = True

    # static method
    def run_file(self, path):
        file = open(path, "r")
        source = file.read()
        file.close()

        self.run(source)

        if self.had_error:
            sys.exit(65)
        elif self.had_runtime_error:
            sys.exit(70)


def main():
    program = Lox()
    # The first argument in sys.argv will always be Lox.py
    num_args = len(sys.argv) - 1
    if num_args > 1:
        print("Usage: pylox [script]")
        os._exit(64)
    elif num_args == 1:
        program.run_file(sys.argv[1])
    else:
        program.run_prompt()


if __name__ == "__main__":
    main()
