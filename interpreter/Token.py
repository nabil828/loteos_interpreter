class Token:

    def __init__(self, token_type, lexeme, literal, line):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return str(self.token_type) + " " + str(self.lexeme) + " " + str(self.literal)

