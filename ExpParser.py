from typing import Any

from ClassesAndFunctions import *
from ClassesAndFunctions import Node


class ParserClass:
    def __init__(self, token_list):
        self._token_list = iter(token_list)
        self.counter = -1
        self.advance()

    def raise_error(self, message):
        """
        This function raises an error. It is called in the parse() function.
        """
        raise SyntaxError(message)

    def advance(self):
        """
        This function advances the current token in the token list
        until it reaches EOL Token. It also updates a counter for error
        handling purposes (updating messages).
        """
        self.current_token = next(self._token_list)
        if self.current_token.type != TokenTypes.EOL:
            self.counter += len(self.current_token.value)

    def parse(self) -> Node | None | Any:
        """
        Grammar for this reverse-descent parser in Extended Backus-Naur Form (EBNF)
        format that obey the restrictions of LL(1):
            S = E
            E = T { (+ | -) T}
            T = F { (* | / | %) F}
            F = [+|-] U
            U = X{^U}
            X = I{!}
            I = "(" E ")" | Func "(" [ E {,E} ] ")" | C | N
            Func = FUNCTION
            C = CONSTANT
            N = NUMBER
        """
        if self.current_token.value is None:
            return None

        result = self.E()

        if self.current_token.value is not None:
            self.raise_error(f"Expected an operator instead of {self.current_token.value} at {self.counter}")

        return result

    def E(self) -> Node | Any:
        result = self.T()

        while (self.current_token.value is not None and
               self.current_token.value in (OPERATORS_DICT["+"].sym,
                                            OPERATORS_DICT["-"].sym)):
            if self.current_token.value == OPERATORS_DICT["+"].sym:
                self.advance()
                result_2 = self.T()
                result = Node(OPERATORS_DICT["+"], result, result_2)
            elif self.current_token.value == OPERATORS_DICT["-"].sym:
                self.advance()
                result_2 = self.T()
                result = Node(OPERATORS_DICT["-"], result, result_2)

        return result

    def T(self) -> Node | Any:
        result = self.F()

        while (self.current_token.value is not None and
               self.current_token.value in (OPERATORS_DICT["*"].sym,
                                            OPERATORS_DICT["/"].sym,
                                            OPERATORS_DICT["%"].sym)):
            if self.current_token.value == OPERATORS_DICT["*"].sym:
                self.advance()
                result_2 = self.F()
                result = Node(OPERATORS_DICT["*"], result, result_2)
            elif self.current_token.value == OPERATORS_DICT["/"].sym:
                self.advance()
                result_2 = self.F()
                result = Node(OPERATORS_DICT["/"], result, result_2)
            elif self.current_token.value == OPERATORS_DICT["%"].sym:
                self.advance()
                result_2 = self.F()
                result = Node(OPERATORS_DICT["%"], result, result_2)

        return result

    def F(self) -> Node | Any:
        if self.current_token.value == OPERATORS_DICT["+"].sym:
            self.advance()
            result_1 = self.U()
            result = Node(OPERATORS_DICT["+"], result_1)
        elif self.current_token.value == OPERATORS_DICT["-"].sym:
            self.advance()
            result_1 = self.U()
            result = Node(OPERATORS_DICT["-"], result_1)
        else:
            result = self.U()

        return result

    def U(self) -> Node | Any:
        result = self.X()

        while (self.current_token.value is not None and
               self.current_token.value == OPERATORS_DICT["^"].sym):
            if self.current_token.value == OPERATORS_DICT["^"].sym:
                self.advance()
                result_2 = self.U()
                result = Node(OPERATORS_DICT["^"], result, result_2)

        return result

    def X(self) -> Node | Any:
        result = self.I()

        while (self.current_token.value is not None and
               self.current_token.value == OPERATORS_DICT["!"].sym):
            if self.current_token.value == OPERATORS_DICT["!"].sym:
                self.advance()
                result = Node(OPERATORS_DICT["!"], result)

        return result

    def I(self) -> Node | Any:
        if self.current_token.type == TokenTypes.LPAREN:
            self.advance()
            result = self.E()
            if self.current_token.type != TokenTypes.RPAREN:
                self.raise_error(f"\")\" not present at index {self.counter + 1}")
            self.advance()
        elif self.current_token.type == TokenTypes.VARIABLE:
            if self.current_token.value in VARIABLES_DICT.keys():
                result = Node(VARIABLES_DICT[self.current_token.value])
                self.advance()
            else:
                result = Node(VariableObject(self.current_token.value, None))
                self.advance()
                #self.raise_error(f"Invalid variable name {self.current_token.value}.")
        elif self.current_token.type == TokenTypes.FUNCTION:
            if self.current_token.value in FUNCTIONS_DICT.keys():
                function = self.current_token.value
                self.advance()
                if self.current_token.type == TokenTypes.LPAREN:
                    self.advance()
                    if self.current_token.type == TokenTypes.RPAREN:
                        arg_list = []
                    else:
                        arg_list = [self.E()]
                    while (self.current_token.value is not None and
                           self.current_token.type == TokenTypes.COMMA):
                        self.advance()
                        arg_list.append(self.E())
                    if self.current_token.type == TokenTypes.RPAREN:
                        self.advance()
                        if len(arg_list) != FUNCTIONS_DICT[function].argc:
                            self.raise_error(f"Expected arguments of {FUNCTIONS_DICT[function].argc} for "
                                             f"function \"{function}\". Got {len(arg_list)} instead.")
                        if function == "sum" or function == "product":
                            result = AggregationNode(*arg_list, function_obj=FUNCTIONS_DICT[function])
                        else:
                            result = Node(FUNCTIONS_DICT[function], *arg_list)
                    else:
                        self.raise_error(f"No closing parenthesis after function {function}.")
                else:
                    self.raise_error(f"No \"(\" after function name {function}.")
            else:
                self.raise_error(f"Invalid function {self.current_token.value}.")
        elif self.current_token.type == TokenTypes.NUMBER:
            try:
                float_number = float(self.current_token.value)
                result = Node(float_number)
            except ValueError:
                self.raise_error(f"Invalid real number {self.current_token.value}.")
            self.advance()
        else:
            self.raise_error(f"Expected a number instead of {self.current_token.value} at index {self.counter}")

        return result



#raw_expression = "sin(85+5+*i)"
#lexer = LexerClass(raw_expression)
#token_list = lexer.tokenize()
#parser = ParserClass(token_list)
#ast = parser.parse()
#print(ast)














