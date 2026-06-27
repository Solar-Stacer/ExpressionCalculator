from cmath import sin, cos, tan, sinh, cosh, tanh, asin, acos, atan, log, isnan, isinf
from math import factorial, comb, floor, ceil
from cmath import pi, e
from random import randint
import os

class BoundException(Exception):
    pass

class InvalidSyntaxException(Exception):
    pass

class InvalidFunctionException(Exception):
    pass

class InvalidArgumentException(Exception):
    pass

class EmptyArgumentException(Exception):
    pass

class InvalidArgumentType(Exception):
    pass

class InvalidResult(Exception):
    pass


def check_asso(op):
    if op == "^":
        return False
    else:
        return True

def check_prec(op1, op2):
    functions = ["sin", "cos", "tan", "csc", "sec", "cot", "ln", "sinh", "cosh", "tanh", 
                 "csc", "sec", "cot", "asin", "acos", "atan", "max", "comb", "sum", "log",
                 "floor", "ceil", "rand"]
    op1_val = 0
    op2_val = 0
    if op1 in functions:
        op1_val = 0
    if op2 in functions:
        op2_val = 0
    if op1 in "+-":
        op1_val = 1
    if op2 in "+-":
        op2_val = 1
    if op1 in "*×/÷":
        op1_val = 2
    if op2 in "*×/÷":
        op2_val = 2
    if op1 in "^":
        op1_val = 3
    if op2 in "^":
        op2_val = 3
    if op1 in "!":
        op1_val = 4
    if op2 in "!":
        op2_val = 4

    if op2_val > op1_val:
        return 1
    elif op2_val < op1_val:
        return -1
    elif op2_val == op1_val:
        return 0

def find_func_indices(expression, functions):
    func_indices = []
    name_stack = ""

    for a in range(len(expression)):
        name_stack += expression[a]
        for b in range(len(functions)):
            if (functions[b]+"(") in name_stack:
                func_indices.append(a - len(functions[b]))
                name_stack = ""
                break
    
    return func_indices

def sum(exp, ub, lb, ang_unit):
    result = 0

    if lb > ub:
        raise BoundException("The lower bound is larger than the upper bound.")

    for i in range(lb, ub+1):
        simpli_exp = validate_exp(exp)
        square_brac_indices = [i for i, ch in enumerate(simpli_exp) if ch in "[]"]
        if square_brac_indices:
            max_right_squ_index = max(square_brac_indices)
            max_left_squ_index = min(square_brac_indices)
            left_chunk = simpli_exp[:max_left_squ_index]
            middle_chunk = simpli_exp[max_left_squ_index:max_right_squ_index+1]
            right_chunk = simpli_exp[max_right_squ_index+1:]
            left_chunk_ch = left_chunk.replace("x", str(i))
            left_chunk_ch = left_chunk_ch.replace("ma"+str(i), "max")
            right_chunk_ch = right_chunk.replace("x", str(i))
            right_chunk_ch = right_chunk_ch.replace("ma"+str(i), "max")
            simpli_exp_ch = left_chunk_ch + middle_chunk + right_chunk_ch
        else:
            simpli_exp_ch = simpli_exp.replace("x", str(i))
            simpli_exp_ch = simpli_exp_ch.replace("ma"+str(i), "max")
            if i < 0:
                simpli_exp_ch = validate_exp(simpli_exp_ch)
        rpn_exp = rpn_parser(simpli_exp_ch)
        result += evaluate(rpn_exp, ang_unit)
    return result

def validate_exp(expression):
    if "pi" in expression:
        expression = expression.replace("pi", "π")

    j = 0
    if " " in expression:
        expression = expression.replace(" ", "")
    while True:
        letter = expression[j]
        if letter == ",":
            expression = expression[:j+1] + " " + expression[j+1:]
        j += 1
        length = len(expression)
        if j == length:
            break

    brac_indices = [i for i, ch in enumerate(expression) if ch in "()[]"]
    if len(brac_indices) % 2 == 1:
        raise InvalidSyntaxException("At least one unmatched bracket is present.")
    
    functions = ["sin", "cos", "tan", "sinh", "cosh", "tanh", "csc", "sec", "cot", 
                 "asin", "acos", "atan", "ln", "max", "comb", "sum", "log", "rand", "abs", "floor", "ceil"]
    func_indices = []
    name_stack = ""
    for k in range(len(functions)):
        func_indices = []
        for i in range(len(expression)):
            name_stack += expression[i]
            if (functions[k]+"(") in name_stack:
                func_indices.append(i - len(functions[k]))
                name_stack = ""
        if name_stack != "":
            name_stack = ""
        for j in range(len(func_indices)):
            right_left_delta = 0
            arg = 0
            right_brac_index = 0
            left_brac_index = 0
            comma_indices = []
            exp_chunk = expression[func_indices[j]:]
            for i in range(len(exp_chunk)):
                left_brac_index = len(functions[k])
                if exp_chunk[i] in "([":
                    right_left_delta += 1
                    if right_left_delta == 0 and i != 0:
                        right_brac_index = i
                        break
                if exp_chunk[i] in ")]":
                    right_left_delta -= 1
                    if right_left_delta == 0 and i != 0:
                        right_brac_index = i
                        break
                if exp_chunk[i] == "," and right_left_delta == 1:
                    comma_indices.append(i)
                    arg += 1
            arg += 1
            if right_left_delta != 0:
                raise InvalidSyntaxException("At least one unmatched bracket is present.")
            if arg != 1 and functions[k] in ["sin", "cos", "tan", "sinh", "cosh", "tanh", "csc", "sec", "cot", "asin", "acos", "atan", "ln", "abs", "floor", "ceil"]:
                raise InvalidArgumentException(f"Function '{functions[k]}' only takes 1 argument")
            elif arg == 1 and functions[k] in ["sin", "cos", "tan", "sinh", "cosh", "tanh", "csc", "sec", "cot", "asin", "acos", "atan", "ln", "abs", "floor", "ceil"]:
                if exp_chunk[left_brac_index+1:right_brac_index] == "":
                    raise EmptyArgumentException(f"Function '{functions[k]}' argument is empty.")
            if arg != 2 and functions[k] in ["max", "comb", "log", "rand"]:
                raise InvalidArgumentException(f"Function '{functions[k]}' only takes 2 arguments")
            elif arg == 2 and functions[k] in ["max", "comb", "log", "rand"]:
                if exp_chunk[left_brac_index+1:comma_indices[0]] == "":
                    raise EmptyArgumentException(f"Function '{functions[k]}' 1st argument is empty.")
                if exp_chunk[comma_indices[0]+1:right_brac_index] == "":
                    raise EmptyArgumentException(f"Function '{functions[k]}' 2nd argument is empty.")
            if arg != 3 and functions[k] == "sum":
                raise InvalidArgumentException(f"Function '{functions[k]}' only takes 3 arguments")
            elif arg == 3 and functions[k] == "sum":
                if exp_chunk[left_brac_index+1:comma_indices[0]] == "":
                    raise EmptyArgumentException(f"Function '{functions[k]}' 1st argument is empty.")
                if exp_chunk[comma_indices[0]+1:comma_indices[1]] == "":
                    raise EmptyArgumentException(f"Function '{functions[k]}' 2nd argument is empty.")
                if exp_chunk[comma_indices[1]+1:right_brac_index] == "":
                    raise EmptyArgumentException(f"Function '{functions[k]}' 3rd argument is empty.")
                
    while True:
        plus_minus_indices = [i for i, ch in enumerate(expression) if ch == "-" or ch == "+"]
        plus_minus_indices_split = []
        if plus_minus_indices:
            temp = [plus_minus_indices[0]]
            for num in plus_minus_indices[1:]:
                if num == temp[-1] + 1:
                    temp.append(num)
                else:
                    if len(temp) > 1:
                        plus_minus_indices_split.append(temp)
                    temp = [num]
            if len(temp) > 1:
                plus_minus_indices_split.append(temp)
            if plus_minus_indices_split:
                minus_count = expression[plus_minus_indices_split[0][0]:plus_minus_indices_split[0][-1]+1].count("-")
                if minus_count % 2 == 0:
                    expression = expression.replace(expression[plus_minus_indices_split[0][0]:plus_minus_indices_split[0][-1]+1], "+")
                else:
                    expression = expression.replace(expression[plus_minus_indices_split[0][0]:plus_minus_indices_split[0][-1]+1], "-")
            else:
                break
        else:
            break

    j = 0
    while True:
        minus_indices = [i for i, ch in enumerate(expression) if ch in "-"]
        if minus_indices:
            if minus_indices[j] != 0:
                if expression[minus_indices[j]-1] not in "1234567890)eπjx*/":
                    expression = expression[:minus_indices[j]] + "0" + expression[minus_indices[j]:]
        else:
            break
        j += 1
        if j == len(minus_indices):
            break

    j = 0
    while True:
        left_brac_indices = [i for i, ch in enumerate(expression) if ch in "("]
        if left_brac_indices:
            if left_brac_indices[j] != 0:
                if expression[left_brac_indices[j]+1] in "+-":
                    expression = expression[:left_brac_indices[j]+1] + "0" + expression[left_brac_indices[j]+1:]
                if expression[left_brac_indices[j]-1] in "1234567890ejπ)":
                    expression = expression[:left_brac_indices[j]] + "*" + expression[left_brac_indices[j]:]
                if expression[left_brac_indices[j]-1] == "x":
                    if left_brac_indices[j]-1 != 0:
                        if expression[left_brac_indices[j]-2] != "a":
                            expression = expression[:left_brac_indices[j]] + "*" + expression[left_brac_indices[j]:]
        else:
            break
        j += 1
        if j == len(left_brac_indices):
            break

    j = 0
    while True:
        right_brac_indices = [i for i, ch in enumerate(expression) if ch in ")"]
        if right_brac_indices:
                if right_brac_indices[j] != len(expression)-1:
                    if expression[right_brac_indices[j]+1] in "123456789":
                        expression = expression[:right_brac_indices[j]+1] + "*" + expression[right_brac_indices[j]+1:]
                    if expression[right_brac_indices[j]+1].isalpha():
                        expression = expression[:right_brac_indices[j]+1] + "*" + expression[right_brac_indices[j]+1:]
        else:
            break
        j += 1
        if j == len(right_brac_indices):
            break

    j = 0
    while True:
        left_sqrt_brac_indices = [i for i, ch in enumerate(expression) if ch in "["]
        if left_sqrt_brac_indices:
                if expression[left_sqrt_brac_indices[j]-1] != "(":
                    raise InvalidSyntaxException("The first argument of the 'sum' function is invalid. There must not be any elements outside [].")
        else:
            break
        j += 1
        if j == len(left_sqrt_brac_indices):
            break

    j = 0
    while True:
        right_sqrt_brac_indices = [i for i, ch in enumerate(expression) if ch in "]"]
        if right_sqrt_brac_indices:
                if expression[right_sqrt_brac_indices[j]+1] != ",":
                    raise InvalidSyntaxException("The first argument of the 'sum' function is invalid. There must not be any elements outside [].")
        else:
            break
        j += 1
        if j == len(right_sqrt_brac_indices):
            break

    j = 0
    while True:
        func_indices = find_func_indices(expression, functions)
        if func_indices:
            if func_indices[j] != 0:
                if expression[func_indices[j]-1] in "1234567890ejπx":
                    expression = expression[:func_indices[j]] + "*" + expression[func_indices[j]:]
        else:
            break
        j += 1
        if j == len(func_indices):
            break
    
    j = 0
    while True:
        const_indices = [n for n, ch in enumerate(expression) if ch in {'π', 'e', 'j', 'x'}]
        func_indices = find_func_indices(expression, functions)
        if const_indices:
            const_indices = [n for n, ch in enumerate(expression) if ch in {'π', 'e', 'j', 'x'}]
            if const_indices[j] != 0:
                if expression[const_indices[j]-1] in "1234567890ejπx":
                    expression = expression[:const_indices[j]] + "*" + expression[const_indices[j]:]
            const_indices = [n for n, ch in enumerate(expression) if ch in {'π', 'e', 'j', 'x'}]
            if const_indices[j] != len(expression)-1:
                if expression[const_indices[j]+1] in "1234567890ejπx":
                    expression = expression[:const_indices[j]+1] + "*" + expression[const_indices[j]+1:]
                for i in range(len(func_indices)):
                    if const_indices[j]+1 == func_indices[i]:
                        expression = expression[:const_indices[j]+1] + "*" + expression[const_indices[j]+1:]
        else:
            break
        j += 1
        if j == len(const_indices):
            break
    
    j = 0
    while True:
        factorial_indices = [n for n in range(len(expression)) if expression.find('!', n) == n]
        if factorial_indices:
            if factorial_indices[j] != len(expression)-1:
                factorial_indices = [n for n in range(len(expression)) if expression.find('!', n) == n]
                if expression[factorial_indices[j]+1] in "1234567890ejπx":
                    expression = expression[:factorial_indices[j]+1] + "*" + expression[factorial_indices[j]+1:]
                for i in range(len(func_indices)):
                    if factorial_indices[j]+1 == func_indices[i]:
                        expression = expression[:factorial_indices[j]+1] + "*" + expression[factorial_indices[j]+1:]
        else:
            break
        j += 1
        if j == len(factorial_indices):
            break

    if expression[0] in "+-":
        expression = "0" + expression
    
    return expression

def rpn_parser(expression):
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "j"]
    operators = ["+", "-", "*", "×", "/", "÷", "^", "!"]
    functions = ["sin", "cos", "tan", "sinh", "cosh", "tanh",
                 "csc", "sec", "cot", "asin", "acos", "atan",
                 "ln", "max", "comb", "sum", "log", "rand", "abs", "floor", "ceil"]
    constants = ["π", "e", "x"]
    output = []
    stack = []
    name_stack = ""
    num_stack = ""
    sum_exp = False
    sum_exp_stack = ""
    operand_flag = False
    
    for i in range(len(expression)):
        token = expression[i]
        
        square_brac_indices = [i for i, ch in enumerate(expression) if ch in "[]"]
        if square_brac_indices: 
            if token in "[":
                sum_exp = True
            if token in "]" and i == max(square_brac_indices):
                output.append(sum_exp_stack)
                sum_exp_stack = ""
                sum_exp = False
        
        if sum_exp:
            if i != min(square_brac_indices):
                sum_exp_stack += token
        else:
            if token in numbers:
                if name_stack != "":
                    raise InvalidFunctionException(f"The variable {name_stack} is not defined.")
                num_stack += token
                operand_flag = True

            elif token in "(":
                for l in range(len(functions)):
                    if name_stack == functions[l]:
                        stack.append(functions[l])
                        name_stack = ""
                        break
                if name_stack != "":
                    raise InvalidFunctionException(f"The function {name_stack} is not defined.")
                if num_stack != "":
                    output.append(complex(num_stack) if complex(num_stack).imag != 0 else float(num_stack))
                    num_stack = ""
                stack.append(token)

            elif token in ")":
                if num_stack != "":
                    output.append(complex(num_stack) if complex(num_stack).imag != 0 else float(num_stack))
                    num_stack = ""
                if name_stack != "":
                    raise InvalidFunctionException(f"The variable {name_stack} is not defined.")
                if operand_flag == False:
                    raise InvalidSyntaxException(f"Invalid syntax: At index {i-1} of the expression, an operand '{expression[i-1]}' instead of a number.")
                j = len(stack)-1
                while True:
                    if stack[j] != "(":
                        sym = stack.pop(j)
                        output.append(sym)
                    else:
                        if stack[j-1] in functions:
                            sym = stack.pop(j-1)
                            output.append(sym)
                        sym = stack.pop(len(stack)-1)
                        break
                    j -= 1

            elif token in operators:
                if num_stack != "":
                    output.append(complex(num_stack) if complex(num_stack).imag != 0 else float(num_stack))
                    num_stack = ""
                if name_stack != "":
                    raise InvalidFunctionException(f"The variable {name_stack} is not defined.")
                if operand_flag == True and token == "!":
                    operand_flag = True
                else:
                    if operand_flag == False:
                        raise InvalidSyntaxException(f"Invalid syntax: At index {i} of the expression, an operand '{token}' instead of a number.")
                    operand_flag = False
                o1 = token
                if len(stack) == 0:
                    stack.append(token)
                else:
                    k = len(stack)-1
                    if check_prec(o1, stack[k]) == -1:
                        stack.append(token)
                    else:
                        while k >= 0:
                            o2 = stack[k]
                            if o2 != "(":
                                if check_prec(o1, o2) == 1 or (check_prec(o1, o2) == 0 and check_asso(o1)):
                                    sym = stack.pop(k)
                                    output.append(sym)
                                k -= 1
                            else:
                                break
                        stack.append(token)

            elif token.isalpha():
                name_stack += token
            
            elif token in ",":
                if num_stack != "":
                    output.append(complex(num_stack) if complex(num_stack).imag != 0 else float(num_stack))
                    num_stack = ""
                k = len(stack)-1
                while k >= 0:
                    o2 = stack[k]
                    if o2 != "(":
                        sym = stack.pop(k)
                        output.append(sym)
                        k -= 1
                    else:
                        break
            
            elif token in " []":
                pass
            
            else:
                raise InvalidSyntaxException(f"Invalid character found: '{token}'")
            
            if name_stack == constants[0]:
                output.append(float(pi))
                name_stack = ""
                operand_flag = True
            elif name_stack == constants[1]:
                output.append(float(e))
                name_stack = ""
                operand_flag = True
            elif name_stack == constants[2] and name_stack not in "max":
                output.append(float(e))
                name_stack = ""
                operand_flag = True
                
    if num_stack != "":
        output.append(complex(num_stack) if complex(num_stack).imag != 0 else float(num_stack))
    if name_stack != "":
        raise InvalidSyntaxException(f"'{name_stack}' is not defined.")
    if not operand_flag:
        raise InvalidSyntaxException(f"One of the operand is not enclosed with number(s).")
    stack = stack[::-1]
    output += stack
    return output

def evaluate(rpn_expression, ang_unit):
    output = []
    for j in range(len(rpn_expression)):
        sym1 = 0.0
        sym2 = 0.0
        token = rpn_expression[j]
        if type(token) is float or type(token) is complex:
            output.append(token)
        elif type(token) is str:
            i = len(output)
            if token in "+-*×/÷^":
                sym1 = output.pop(i-1)
                sym2 = output.pop(i-2)
                if token in "+":
                    output.append(sym2 + sym1)
                elif token in "-":
                    output.append(sym2 - sym1)
                elif token in "*×":
                    output.append(sym2 * sym1)
                elif token in "/÷":
                    output.append(sym2 / sym1)
                elif token in "^":
                    output.append(sym2 ** sym1)
            elif "x" in token and token not in "max":
                output.append(token)
            else:
                if token == "!":
                    sym1 = output.pop(i-1)
                    if sym1.imag != 0 or sym1 < 0 or not sym1.is_integer():
                        raise InvalidArgumentType("The argument for factorial '!' is only positive integers.")
                    output.append(factorial(int(sym1)))

                elif token == "sin":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        sym1 = sym1*(pi/180)
                    output.append(sin(sym1))
                    if isnan(sin(sym1)) or isinf(sin(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "cos":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        sym1 = sym1*(pi/180)
                    output.append(cos(sym1))
                    if isnan(cos(sym1)) or isinf(cos(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "tan":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        sym1 = sym1*(pi/180)
                    output.append(tan(sym1))
                    if isnan(tan(sym1)) or isinf(tan(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "ln":
                    sym1 = output.pop(i-1)
                    output.append(log(sym1))
                    if isnan(log(sym1)) or isinf(log(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "sinh":
                    sym1 = output.pop(i-1)
                    output.append(sinh(sym1))
                    if isnan(sinh(sym1)) or isinf(sinh(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "cosh":
                    sym1 = output.pop(i-1)
                    output.append(cosh(sym1))
                    if isnan(cosh(sym1)) or isinf(cosh(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "tanh":
                    sym1 = output.pop(i-1)
                    output.append(tanh(sym1))
                    if isnan(tanh(sym1)) or isinf(tanh(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "csc":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        sym1 = sym1*(pi/180)
                    output.append(1/sin(sym1))
                    if isnan(1/sin(sym1)) or isinf(1/sin(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "sec":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        sym1 = sym1*(pi/180)
                    output.append(1/cos(sym1))
                    if isnan(1/cos(sym1)) or isinf(1/cos(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "cot":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        sym1 = sym1*(pi/180)
                    output.append(1/tan(sym1))
                    if isnan(1/tan(sym1)) or isinf(1/tan(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "asin":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        output.append(asin(sym1)*(180/pi))
                    else:
                        output.append(asin(sym1))
                    if isnan(asin(sym1)) or isinf(asin(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "acos":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        output.append(acos(sym1)*180/pi)
                    else:
                        output.append(acos(sym1))
                    if isnan(acos(sym1)) or isinf(acos(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "atan":
                    sym1 = output.pop(i-1)
                    if ang_unit == "deg":
                        output.append(atan(sym1)*180/pi)
                    else:
                        output.append(atan(sym1))
                    if isnan(atan(sym1)) or isinf(atan(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
                elif token == "abs":
                    sym1 = output.pop(i-1)
                    output.append(abs(sym1))
                    if isnan(abs(sym1)) or isinf(abs(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")

                elif token == "floor":
                    sym1 = output.pop(i-1)
                    if abs(sym1.imag) > 0:
                        raise InvalidArgumentType("The argument(s) for 'floor' is/are a complex number.")
                    output.append(floor(sym1))
                    if isnan(abs(sym1)) or isinf(abs(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")

                elif token == "ceil":
                    sym1 = output.pop(i-1)
                    if abs(sym1.imag) > 0:
                        raise InvalidArgumentType("The argument(s) for 'ceil' is/are a complex number.")
                    output.append(ceil(sym1))
                    if isnan(abs(sym1)) or isinf(abs(sym1)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")

                elif token == "max":
                    sym1 = output.pop(i-1)
                    sym2 = output.pop(i-2)
                    if abs(sym1.imag) > 0 or abs(sym2.imag) > 0:
                        raise InvalidArgumentType("The argument(s) for 'max' is/are a complex number.")
                    output.append(max(sym1, sym2))

                elif token == "comb":
                    sym1 = output.pop(i-1)
                    sym2 = output.pop(i-2)
                    if abs(sym1.imag) > 0 or abs(sym2.imag) > 0 or not sym2.is_integer() or not sym1.is_integer():
                        raise InvalidArgumentType("The argument(s) for 'comb' is/are an invalid number.")
                    output.append(comb(sym2, sym1))

                elif token == "rand":
                    sym1 = output.pop(i-1)
                    sym2 = output.pop(i-2)
                    if abs(sym1.imag) > 0 or abs(sym2.imag) > 0 or not sym2.is_integer() or not sym1.is_integer():
                        raise InvalidArgumentType("The argument(s) for 'rand' is/are an invalid number.")
                    output.append(randint(sym2 , sym1))

                elif token == "sum":
                    lb = output.pop(i-1)
                    ub = output.pop(i-2)
                    if abs(lb.imag) > 0 or abs(ub.imag) > 0 or not (lb.real).is_integer() or not (ub.real).is_integer():
                        raise InvalidArgumentType("The bound(s) is/are an invalid number.")
                    exp = output.pop(i-3)
                    output.append(sum(str(exp), int(ub), int(lb), ang_unit))

                elif token == "log":
                    base = output.pop(i-1)
                    base = complex(base) if complex(base).imag != 0 else float(base.real)
                    sym1 = output.pop(i-2)
                    output.append(log(sym1, base))
                    if isnan(log(sym1, base)) or isinf(log(sym1, base)):
                        raise InvalidResult("An invalid result is present: inf or NaN value is present")
                    
    result = output.pop(0)
    return result

def main():
    ang_unit = "rad"
    while True:
        print("Supported functions: \n"
              "\tsin(complex: x)\n"
              "\tcos(complex: x)\n"
              "\ttan(complex: x), x ≠ π/2\n"
              "\tsinh(complex: x)\n"
              "\tcosh(complex: x)\n"
              "\ttanh(complex: x)\n"
              "\tasin(complex: x)\n"
              "\tacos(complex: x)\n"
              "\tatan(complex: x)\n"
              "\tcsc(complex: x)\n"
              "\tsec(complex: x)\n"
              "\tcot(complex: x)\n"
              "\tsec(complex: x)\n"
              "\tabs(complex: x)\n"
              "\tlog(complex: x, complex: base), base ≠ 0\n"
              "\tln(complex: x)\n"
              "\tfloor(real: x)\n"
              "\tceil(real: x)\n"
              "\trand(int: x, int: y), y > x\n"
              "\tmax(int: x, int: y)\n"
              "\tcomb(int: n, int: k), k ≥ 0, n ≥ 0, n ≥ k\n"
              "\tsum( [str: expression (in terms of x)] , int: upper_bound, int: lower_bound)\n"
              "\t\t example: sum( [x+3] , 4, 2)\n")
        print(f"For complex numbers, the imaginary unit is denoted by 'j', not 'i'.")
        print(f"Angle units are in {"RADIANS" if ang_unit == "rad" else "DEGREES"}. To change, input 'deg' to change to degrees or 'rad' to change back to radians.")
        expression = input(f"Enter your expression: ").lower()
        if expression in ["deg", "degree", "degrees"]:
            ang_unit = "deg"
            os.system('cls' if os.name == 'nt' else 'clear')
        elif expression in ["rad", "radian", "radians"]:
            ang_unit = "rad"
            os.system('cls' if os.name == 'nt' else 'clear')
        else:
            break

    simpli_exp = validate_exp(expression)
    print(f"Simplified Infix: {simpli_exp}")

    rpn_expression = rpn_parser(simpli_exp)
    print(f"Expression (Postfix Notation): {rpn_expression}")

    result = evaluate(rpn_expression, ang_unit)
    if result.imag == 0 or abs(result.imag) <= 1e-7:
        result = result.real
        if float(result).is_integer():
            result = int(result)
            print(f"Evaluation: {result}")
        else:
            print(f"Evaluation: {float(format(result, '.8f'))}")
    elif result.real == 0 or abs(result.real) <= 1e-7:
        result = result.imag
        if float(result).is_integer():
            result = int(result)
            print(f"Evaluation: {result}j")
        else:
            print(f"Evaluation: {float(format(result, '.8f'))}j")
    else:
        print(f"Evaluation: {result}")

try:
    main()
    os.system('pause')
except Exception as e:
    import traceback
    summary = traceback.extract_tb(e.__traceback__)
    last_frame = summary[-1]

    line_number = last_frame.lineno
    function_name = last_frame.name
    text = last_frame.line

    print(f"\nError at line {line_number} in {function_name}()")
    #print(f"Code line: {text}")
    print(f"Error message: {e}\n")
    os.system('pause')


# expression = "log(6/2, 5)sin(3log(5,8))+sum([log(x,5)], 6, abs(-2))" # 4.586847055
# expression = "sum([log(x,5)], 6, -1)" # NaN / inf error
# expression = "-log(6/2,(-5)) -(4)(-3)" # 11.85809284 + 0.2770001153j
# expression = "tanh(4j+3)ej2sinh(6*cosh(10^(-23)))jpi-3log(2*3*25, 5.65) + esec(2*10^(-3)) + max(20^2,20/3+--+-+-8)" # −3053.560 − 16.909j
# expression = "3max(-21,-20)" # -60
# expression = "log(comb(25/5,6*3/(3*2))!,10)log(comb(25/5,6*3/(3*2))!tanh(3),10)"  #43.016368
# expression = "sum([x+sum([4x^2+7sum([(max(x,2))!], 3,2)], 6, 2)], 7, 2)" #3867
# expression = "5*sum(4,14, sin(23))" #invalid arg error
# expression = "sum([max(3,max(x,4))], 7,2)" #380
# expression = "4*5*5*sin(3)*(sin(sin(e+))-pi)*3" # operand error
# expression = "pi/2 + jln(j(3)+(1-(3)^2)^(1/2))" # 1.76274717j
# expression = "4!^2"
# print(f"Expression (Infix Notation): {expression}")





