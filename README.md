# Expression Calculator
This is a Python program that takes an input of an infix expression and outputs a result. The program supports complex calculations, summations and products of expressions. The program only supports infix expressions so expressions such as "8(6)" even though valid algebraically, is not a valid infix expression.

## Implementation Details
The current implementation tokenizes the raw input, parses the token stream, and then evaluates the resulting AST (Abstract Syntax Tree) produced by the parser. The parser is Recursive Descent and thus is directly based upon an LL(1) Grammar.

## `_old`
This folder contains the first attempt, i.e. the earliest implementation of this program using Shunting Yard Algorithm. The old implementation consist of a lot of string manipulation and is generally not a consistent code to work with.

## Running
To run the program, all the dependencies in requirements.txt file must be installed.
