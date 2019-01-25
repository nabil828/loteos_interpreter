import sys
import os
import scanner


class lox:
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
        obj = scanner.Scanner(source)
        tokens = obj.scan_tokens()

        for token in tokens:
            print token

    # static method
    def error(self, line, message):
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
    program = lox()
    # The first argument in sys.argv will alwyas be lox.py
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
