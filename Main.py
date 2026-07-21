from ExpLexer import *
import ClassesAndFunctions
from ExpParser import *

def help(is_radians: bool = True):
    print("/// EXPRESSION CALCULATOR ///")

    print("\n/* Operators")
    for key, value in OPERATORS_DICT.items():
        print(f"\t{key}: {value.operator.__name__}")

    print("\n/* Constants")
    for key, value in VARIABLES_DICT.items():
        print(f"\t{key}: {value}")

    print("\n/* Functions")
    max_key_length = max(len(str(k)) for k in HELP_DICT.keys())
    for key, value in HELP_DICT.items():
        print(f"\t{key:<{max_key_length}}\t| {value}")

    print("\nINPUT MUST BE A VALID INFIX EXPRESSION, I.E. 5(6) AND SUCH ARRANGEMENTS ARE INVALID.")
    print("\nTO PRINT THIS HELP, TYPE: help")
    print(f"TRIGONOMETRIC FUNCTIONS ARE IN [{"RADIANS" if is_radians else "DEGREES"}]. "
          f"TO CHANGE TO {"DEGREES" if is_radians else "RADIANS"}, TYPE: {"deg" if is_radians else "rad"}")

def format_result(result: float | int | complex):
    if result.imag == 0 or abs(result.imag) <= 1e-7:
        result = result.real
        if float(result).is_integer():
            result = int(result)
            return result
        else:
            return float(format(result, '.8f'))
    elif result.real == 0 or abs(result.real) <= 1e-7:
        result = result.imag
        if float(result).is_integer():
            result = int(result)
            return f"{result}j"
        else:
            return f"{float(format(result, '.8f'))}j"
    else:
        result = complex(round(result.real, 8), round(result.imag, 8))
        return result

if __name__ == "__main__":
    help()
    while True:
        try:
            raw_expression = input("\nCalc > ").lower()
            if raw_expression == "help()":
                help(is_radians)
            elif raw_expression in ["deg", "degree", "degrees"]:
                print("CHANGED TO DEGREES")
                ClassesAndFunctions.is_radians = False
            elif raw_expression in ["rad", "radian", "radians"]:
                print("CHANGED TO RADIANS")
                ClassesAndFunctions.is_radians = True
            else:
                lexer = LexerClass(raw_expression)
                token_list = lexer.tokenize()
                parser = ParserClass(token_list)
                ast = parser.parse()
                evaluation = AST_evaluation(ast)

                print("Token Stream:", *token_list, sep="\n\t\t")
                print("\nAbstract Syntax Tree:\t", str(ast))
                print("Evaluation:\t\t\t\t", format_result(evaluation))

        except Exception as e:
            import traceback
            summary = traceback.extract_tb(e.__traceback__)
            last_frame = summary[-1]

            line_number = last_frame.lineno
            function_name = last_frame.name
            text = last_frame.line

            print(f"\nError at line {line_number} in {function_name}()")
            # print(f"Code line: {text}")
            print(f"Error message: {e}")
