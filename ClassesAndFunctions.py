from cmath import *
from enum import Enum
from math import e, pi, floor, ceil
from operator import *
from random import randint
from typing import Callable, Any, Optional

from scipy.special import lambertw, gamma


class TokenTypes(Enum):
    """
    An enum describing types of Tokens as enum members. This is for only lexing and parsing purposes
    since a Token will hold a ",", "(", ")", and all of those are strings and not seperate objects.
    """
    EOL = 0
    NUMBER = 1
    OPERATOR = 2
    VARIABLE = 3
    FUNCTION = 4
    LPAREN = 5
    RPAREN = 6
    COMMA = 7


class Token:
    """
    This Token object will hold enum members from the TokenTypes enum to refer to its type,
    and a character, a number, function names, variable names such as +, sin, 3.4, pi and
    so on. Tokens are only used during the lexing and parsing phase and for building the AST.
    After the parsing phase, the AST will have Node objects which will hold actual objects.
    """

    def __init__(self, typ, string):
        self.type = typ
        self.value = string

    def __str__(self):
        return str(self.type) + " " + "\"" + str(self.value) + "\""

    __repr__ = __str__


class Node:
    """
    This Node object is the fundamental unit of the AST. It will hold a list of child Node objects
    (and not parent Node objects) connected to itself in the AST after parsing, and a value which
    is either a float, OperatorObject, VariableObject, or FunctionObject.
    """

    def __init__(self, obj, *args):
        self.object = obj
        self.child_nodes = args

    def __repr__(self):
        if not self.child_nodes:
            return f"{self.object}"
        if len(self.child_nodes) == 1:
            return f"Tree({self.object}, {repr(self.child_nodes[0])})"
        else:
            return f"Tree({self.object}, Tree({", ".join(repr(element) for element in self.child_nodes)}))"


class AggregationNode(Node):
    """
    This is a special node for aggregation operations such as summations and products that inherits
    from Node class. This node is made to differentiate from other nodes when evaluating the AST as
    this node has a VariableObject whose value need to be changed during aggregation operations.
    """

    def __init__(self, *args, function_obj):
        super().__init__(*args)
        self.child_nodes = args
        self.object = function_obj
        self.expression_node = self.child_nodes[0]
        self.var_obj_node = self.child_nodes[1]
        self.lb_node = self.child_nodes[2]
        self.ub_node = self.child_nodes[3]

    def calc(self):
        return self.object.calc(self.expression_node, self.var_obj_node, self.lb_node, self.ub_node)


class VariableObject:
    """
    This object is instantiated multiple times only in the _DICT data structures. This object
    stores a name of the variable that could be a symbol such as e, pi, etc., and float value. The
    purpose of this object is to be holden to a Node in its Object attribute for evaluation
    in the AST.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name

    __repr__ = __str__


class OperatorObject:
    """
    This object is instantiated multiple times only in the _DICT data structures. This object
    stores a symbol of the operator such as +, -, etc., and the operator function as a callback.
    Some operators that are inherently binary can also act as unary operators such as + and -
    operators. Because of this it stores some information on whether an operator is solely a unary
    operator or both or none, by one boolean. If it is, then its callback is self.operator. If it
    is both then its unary callback is self.unary_operator and its binary callback is self.operator.
    The purpose of this object is to be holden to a Node as its Object attribute for evaluation in the AST.
    """

    def __init__(self, sym: str, operator_function: Callable, is_only_unary: bool,
                 unary_operator: Optional[Callable[[Any], Any]] = None):
        self.sym = sym
        self.is_only_unary = is_only_unary
        self.unary_operator = unary_operator
        self.operator = operator_function

    def calc(self, *args):
        if self.is_only_unary:
            return self.operator(*args)
        else:
            if len(args) == 1:
                if self.unary_operator is None:
                    raise ValueError(f"No unary operator defined for {self.sym}")
                return self.unary_operator(args[0])
            elif len(args) == 2:
                return self.operator(*args)
            return None

    def __str__(self):
        return self.sym

    __repr__ = __str__


class FunctionObject:
    """
    This object is instantiated multiple times only in the _DICT data structures. This object
    stores a name of the function, the function itself as a callback and the argument count. The
    purpose of this object is to be holden to a Node as its Object attribute for evaluation in the AST.
    """

    def __init__(self, name, function, argc):
        self.name = name
        self.function = function
        self.argc = argc

    def calc(self, *args):
        return self.function(*args)

    def __str__(self):
        return self.name

    __repr__ = __str__


class AggregationFunctionError(Exception):
    pass


def AST_evaluation(node: Node, sum_var_node: AggregationNode | None = None) -> int | float | None:
    """
    This function evaluates the entire AST by evaluating child nodes (the operands)
    before their parent nodes (the operators). The first argument is the root node
    of the AST. The second argument is the node with a VariableObject attribute
    from a AggregationNode for evaluating aggregation functions such as summations
    and products since they require reevaluating the AST after setting the variable.
    """
    if isinstance(node, AggregationNode):
        return node.calc()

    if isinstance(node.object, VariableObject):
        if sum_var_node is not None:
            if node.object.name == sum_var_node.object.name:
                node.object.value = sum_var_node.object.value
            elif node.object.name not in VARIABLES_DICT.keys():
                raise ValueError(f"Variable {node.object.name} in the summand is not defined in the sum function.")
        else:
            if node.object.name not in VARIABLES_DICT.keys():
                raise ValueError(f"Variable {node.object.name} is not defined.")

        return node.object.value

    if isinstance(node.object, float) or isinstance(node.object, int):
        if node.object.is_integer():
            node.object = int(node.object)
        return node.object

    if isinstance(node.object, FunctionObject):
        arg_list = []
        for i in range(FUNCTIONS_DICT[node.object.name].argc):
            arg_list.append(AST_evaluation(node.child_nodes[i], sum_var_node))
        return node.object.calc(*arg_list)

    if isinstance(node.object, OperatorObject):
        if OPERATORS_DICT[node.object.sym].is_only_unary:
            return node.object.calc(AST_evaluation(node.child_nodes[0], sum_var_node))
        else:
            if len(node.child_nodes) == 1:
                una_val = AST_evaluation(node.child_nodes[0], sum_var_node)
                return node.object.calc(una_val)
            if len(node.child_nodes) == 2:
                left_val = AST_evaluation(node.child_nodes[0], sum_var_node)
                right_val = AST_evaluation(node.child_nodes[1], sum_var_node)
                return node.object.calc(left_val, right_val)
    return None


def factorial(n):
    """
    A function for evaluating factorials of positive integers, with some
    error correction.
    """
    if n.imag == 0:
        n = n.real
    else:
        raise TypeError("Factorial is undefined for complex numbers.")
    if not n.is_integer():
        raise TypeError("Factorial is undefined for floats.")
    if n < 0:
        raise TypeError("Factorial is undefined for negative integers.")
    if n == 0:
        return 1
    return n * factorial(n - 1)


def product(product_node, var_node, lb_node, ub_node):
    """
    A function for evaluating products of expressions with all the arguments
    being nodes. First is the product node which is a AggregationNode object and
    consist of the AST of the expression. Second is the variable node which is
    a singleton that consist of a VariableObject attribute. Third and forth
    are lower and upper bound nodes which may or may not have AST.
    """
    lower_bound = AST_evaluation(lb_node)
    upper_bound = AST_evaluation(ub_node)
    if lower_bound is not None and upper_bound is not None:
        lower_bound = int(lower_bound)
        upper_bound = int(upper_bound)
    else:
        raise AggregationFunctionError("AST_Evaluation returned None.")

    if var_node.object.name in VARIABLES_DICT.keys():
        raise AggregationFunctionError(f"The second argument of the summation function cannot be a variable defined "
                                       f"for constants, e.g. {", ".join(VARIABLES_DICT.keys())}")

    if upper_bound < lower_bound:
        raise AggregationFunctionError("Lower bound is more than upper bound.")

    if not isinstance(var_node.object, VariableObject):
        raise AggregationFunctionError("The second argument of the summation function is not a single variable.")

    result = 1
    for i in range(lower_bound, upper_bound + 1):
        var_node.object.value = i
        result *= AST_evaluation(product_node, var_node)

    return result


def summation(summand_node, var_node, lb_node, ub_node):
    """
    A function for evaluating summations of summands with all the arguments
    being nodes. First is the summand node which is a AggregationNode object and
    consist of the AST of the summand. Second is the variable node which is
    a singleton that consist of a VariableObject attribute. Third and forth
    are lower and upper bound nodes which may or may not have AST.
    """
    lower_bound = AST_evaluation(lb_node)
    upper_bound = AST_evaluation(ub_node)
    if lower_bound is not None and upper_bound is not None:
        lower_bound = int(lower_bound)
        upper_bound = int(upper_bound)
    else:
        raise AggregationFunctionError("AST_Evaluation returned None.")

    if var_node.object.name in VARIABLES_DICT.keys():
        raise AggregationFunctionError(f"The second argument of the summation function cannot be a variable defined "
                                       f"for constants, e.g. {", ".join(VARIABLES_DICT.keys())}")

    if upper_bound < lower_bound:
        raise AggregationFunctionError("Lower bound is more than upper bound.")

    if not isinstance(var_node.object, VariableObject):
        raise AggregationFunctionError("The second argument of the summation function is not a single variable.")

    result = 0
    for i in range(lower_bound, upper_bound + 1):
        var_node.object.value = i
        result += AST_evaluation(summand_node, var_node)

    return result


is_radians = True


def sine(z):
    if not is_radians:
        return sin(z * pi / 180)
    else:
        return sin(z)


def cosine(z):
    if not is_radians:
        return cos(z * pi / 180)
    else:
        return cos(z)


def tangent(z):
    if not is_radians:
        return tan(z * pi / 180)
    else:
        return tan(z)


def asine(z):
    if not is_radians:
        return asin(z) * 180 / pi
    else:
        return asin(z)


def acosine(z):
    if not is_radians:
        return acos(z) * 180 / pi
    else:
        return acos(z)


def atangent(z):
    if not is_radians:
        return atan(z) * 180 / pi
    else:
        return atan(z)


def csc(z):
    return 1 / sine(z)


def sec(z):
    return 1 / cosine(z)


def cot(z):
    return 1 / tangent(z)


"""
Dictionaries below are to be used during lexing to append objects to every Token's value attribute, 
and during parsing to, first, further differentiate between the functions and the operators and second, 
to append objects to Node's value attribute for evaluation of the AST.
"""

NUMBERS_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]

OPERATORS_DICT = {
    "+": OperatorObject("+", add, False, abs),
    "-": OperatorObject("-", sub, False, neg),
    "*": OperatorObject("*", mul, False),
    "/": OperatorObject("/", truediv, False),
    "^": OperatorObject("^", pow, False),
    "!": OperatorObject("!", factorial, True),
    "%": OperatorObject("%", mod, False)
}

VARIABLES_DICT = {
    "e": VariableObject("e", e),
    "i": VariableObject("i", 1j),
    "pi": VariableObject("pi", pi)
}

"""
To add a function to this calculator, create a FunctionObject with the appropriate arguments and 
callback and add it to this dictionary.
"""
FUNCTIONS_DICT = {
    "abs": FunctionObject("abs", abs, 1),
    "neg": FunctionObject("neg", neg, 1),
    "fac": FunctionObject("fac", factorial, 1),
    "sqrt": FunctionObject("sqrt", sqrt, 1),
    "floor": FunctionObject("floor", floor, 1),
    "ceil": FunctionObject("ceil", ceil, 1),
    "sin": FunctionObject("sin", sine, 1),
    "cos": FunctionObject("cos", cosine, 1),
    "tan": FunctionObject("tan", tangent, 1),
    "csc": FunctionObject("csc", csc, 1),
    "sec": FunctionObject("cos", sec, 1),
    "cot": FunctionObject("tan", cot, 1),
    "sinh": FunctionObject("sinh", sinh, 1),
    "cosh": FunctionObject("cosh", cosh, 1),
    "tanh": FunctionObject("tanh", tanh, 1),
    "asin": FunctionObject("asin", asine, 1),
    "acos": FunctionObject("acos", acosine, 1),
    "atan": FunctionObject("atan", atangent, 1),
    "max": FunctionObject("max", max, 2),
    "rand": FunctionObject("rand", randint, 2),
    "exp": FunctionObject("exp", exp, 1),
    "log": FunctionObject("log", log, 2),
    "lambertw": FunctionObject("lambertw", lambertw, 2),
    "gamma": FunctionObject("gamma", gamma, 1),
    "sum": FunctionObject("sum", summation, 4),
    "product": FunctionObject("product", product, 4)
}

HELP_DICT = {
    "abs(complex: z)": "Returns the absolute value (or modulus) of z.",
    "neg(complex: z)": "Returns the negation of z.",
    "fac(int: n)": "Returns the factorial of n. Only defined for positive integer.",
    "sqrt(complex: z)": "Returns the square root of z.",
    "floor(real: n)": "Returns the floor of n",
    "ceil(real: n)": "Returns the ceil of n",
    "sin(complex: z)": "Returns the sine of z",
    "cos(complex: z)": "Returns the cosine of z",
    "tan(complex: z)": "Returns the tangent of z",
    "csc(complex: z)": "Returns the cosecant of z",
    "sec(complex: z)": "Returns the secant of z",
    "cot(complex: z)": "Returns the cotangent of z",
    "sinh(complex: z)": "Returns the sinh of z",
    "cosh(complex: z)": "Returns the cosh of z",
    "tanh(complex: z)": "Returns the tanh of z",
    "asin(complex: z)": "Returns the asin of z",
    "acos(complex: z)": "Returns the acos of z",
    "atan(complex: z)": "Returns the atan of z",
    "max(float n, float n)": "Returns the maximum of two real numbers",
    "rand(int n, int n)": "Returns the random number between two numbers",
    "exp(complex: z)": "Returns e to the power of z",
    "log(complex: z₁, complex: z₂)": "Returns the logarithm of z₁ to the base z₂",
    "lambertw(complex: z, int: k=0)": "Returns the lambert W function of z with a branche of k which by default is 0.",
    "gamma(complex: z)": "Returns the gamma function of z. Not defined for negative integer",
    "sum(summand, variable, lb, ub)": "Returns the summation of a summand from the lower bound to upper bound",
    " ": "Example: sum(x+4, x, 0, 5) yields 39",
    "product(factor, variable, lb, ub)": "Returns the product of a factor expression from the lower bound to upper bound",
    "  ": "Example: product(x+2, x, 0, 3) yields 120",
}
