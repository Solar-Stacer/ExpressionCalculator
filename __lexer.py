from __classes_and_functions import *

class LexerClass(object):
    def __init__(self, raw_exp):
        self.expression = iter(raw_exp)
        self.token = []
        self.advance()

    def advance(self):
        try:
            self.current_char = next(self.expression)
            if self.current_char.isspace():
                self.advance()
        except StopIteration:
            self.current_char = None

    def tokenize(self) -> Token:
        while self.current_char is not None:
            if self.current_char in NUMBERS_LIST:
                number_buffer = ""
                while self.current_char is not None and self.current_char in NUMBERS_LIST:
                    number_buffer += self.current_char
                    self.advance()
                self.token.append(Token(TokenTypes.NUMBER, number_buffer))
            elif self.current_char in OPERATORS_DICT:
                self.token.append(Token(TokenTypes.OPERATOR, self.current_char))
                self.advance()
            elif self.current_char.isalpha():
                letter_buffer = ""
                while self.current_char is not None and self.current_char.isalpha():
                    letter_buffer += self.current_char
                    self.advance()
                if self.current_char != "(":
                    self.token.append(Token(TokenTypes.VARIABLE, letter_buffer))
                else:
                    self.token.append(Token(TokenTypes.FUNCTION, letter_buffer))
            elif self.current_char == "(":
                self.token.append(Token(TokenTypes.LPAREN, self.current_char))
                self.advance()
            elif self.current_char == ")":
                self.token.append(Token(TokenTypes.RPAREN, self.current_char))
                self.advance()
            elif self.current_char == ",":
                self.token.append(Token(TokenTypes.COMMA, self.current_char))
                self.advance()
            else:
                raise SyntaxError(f"Unexpected character \"{self.current_char}\".")
        self.token.append(Token(TokenTypes.EOL, None))
        return self.token

