# Compilers
A project for the course Compilers at the University of Antwerp during the second semester of academic year of 2021-2022. The group is composed of Jeff Boermans and Thomas Gueutal.

# Scripts
<b>generate.sh</b>: can be called to (re)generate the dependency ANTLR python files.

<b>run.sh</b>: requires exactly one positional argument, namely the file to run the compiler on. Can be called to in one step generate the dependency ANTLR python files, if they do not exist yet, as well as call the main.py file. The script depends on the generate.sh script to generate the dependency ANTLR python files.

An example call of the compiler is ```./run Input/tests/vars.txt```. Please note that the run.sh script should be called from the directory it is located in.

# Test files
Example test files are found in 'Input/tests'.

# Output
Currently, the compiler will only output a .dot, endtree.dot is post-optimization (e.g. literal folding) and begintree.dot is pre-optimization, file into the Output folder, as no LLVM conversion has been completed yet.

# ANTLR runtime
The ANTLR 4 runtime .jar is provided together with this repository. It is found in the 'Input' directory. As such, all scripts refer to that .jar file instead of any pre-installed versions of ANTLR.

# Features

V: Working

-: Partially working with known problems (Explained below)

X: Not working or not implemented

N: not applicable

(blanc): TODO  

M: mandatory feature

O: optional feature

|     | Functionality              | Grammar/AST <br>Status | LLVM status | MIPS status | type | note                                                                                                            |
|-----|----------------------------|------------------------|-------------|-------------|------|-----------------------------------------------------------------------------------------------------------------|
| 1   | Binary Operators           | V                      | V           |             | M    | (except %)                                                                                                      |
|     | Unary + -                  | V                      | -           |             | M    |                                                                                                                 |
|     | brackets                   | V                      | N           | N           | M    | ( )                                                                                                             |
|     | Logical operators          | V                      | V           |             | M    |                                                                                                                 |
|     | Comparison operators       | V                      | V           |             | O    |                                                                                                                 |
|     | Binary %                   | V                      | V           |             | O    |                                                                                                                 |
|     | Constant folding           | V                      | N           | N           | O    |                                                                                                                 |
| 2   | Types int, float, char     | V                      | V           |             | M    |                                                                                                                 |
|     | Types pointers             | V                      | X           |             | M    |                                                                                                                 |
|     | Reserved words             | V                      | N           | N           | M    | int, float, char and const                                                                                      |
|     | Variables                  | V                      | V           |             | M    | declarations, definitions <br> assignments and use in expressions                                               |
|     | Pointer operations         | V                      | X           |             | M    | unary & and *                                                                                                   |
|     | Identifier operations      | V                      | X           |             | O    | unary ++ and --                                                                                                 |
|     | Conversions                | N                      | X           |             | O    |                                                                                                                 |
|     | Constant propagation       | X                      | N           | N           | O    |                                                                                                                 |
|     | Syntax Errors              | X                      | N           | N           | M    |                                                                                                                 |
|     | Semantic Errors            | -                      |             |             | M    |                                                                                                                 |
| 3   | Comments 1                 | V                      | N           | N           | M    | ingore comments                                                                                                 |
|     | Comments 2                 | N                      | X           |             | O    | transfer comments to generated LLVM/MIPS                                                                        |
|     | Comments 3                 | N                      | X           |             | O    | comment after every LLVM/MIPS statement                                                                         |
|     | Printf                     | V                      | N           | N           | M    | Only recognition in input C code                                                                                |
| 4   | Loops                      | V                      | V           |             | M    | for, while                                                                                                      |
|     | Conditionals 1             | V                      | -           |             | M    | if, else                                                                                                        |
|     | Conditionals 2             | X                      | X           |             | O    | switch, case, default                                                                                           |
|     | Jump statements            | V                      | X           |             | M    | continue, break                                                                                                 |
|     | Scopes                     | V                      | V           |             | M    | unnamed scope, loops and conditional scopes                                                                     |
|     | Semantic Analysis          | V                      | N           | N           | M    | variable resolution now depends on scope, first check current scope and only then eclosing scope                |
| 5   | Reserved words             | V                      | V           |             | M    | return, void                                                                                                    |
|     | Scopes                     | V                      | V           |             | M    | function scopes                                                                                                 |
|     | Local and Global variables | -                      | -           |             | M    |                                                                                                                 |
|     | Semantic Analysis 1        | V                      | N           | N           | M    | 1) consistency of return statement with return type <br>2) consistency forward declaration and definition types |
|     | Semantic Analysis 2        | X                      | N           | N           | O    | Check whether all path in the function body end with a return (only for non-void functions)                     |
|     | Optimizations 1            | X                      | X           |             | M    | Do not generate code for unreachable and dead C code (code after a return statement)                            |
|     | Optimizations 2            | X                      | X           |             | M    | Do not generate code for C code after continue or break                                                         |
|     | Optimizations 3            | X                      | X           |             | O    | Do not generate code for unused variables                                                                       |
|     | Optimizations 4            | X                      | X           |             | O    | Do not generate code for conditionals that are never true                                                       |
| 6   | Arrays                     | -                      | X           |             | M    | Array variables, operations on individual array elements                                                        |
|     | Multi-dimensional Arrays 1 | X                      | X           |             | O    | Multi-dimensional array variables                                                                               |
|     | Multi-dimensional Arrays 2 | X                      | X           |             | O    | Assignment of complete arrays or array rows                                                                     |
|     | Dynamic arrays             | X                      | X           |             | O    |                                                                                                                 |
|     | Import                     | V                      | X           |             | M    | Support for import of stdio.h and use of printf and scanf, with sequences with codes d, i, s and c              |

* Unary +, - (LLVM): Unary - works for floats but not for ints.
* Semantic Errors: missing operations of incompatible types, assignment to an rvalue and assignment to const variable
* Conditionals 1 LLVM: Unfinished LLVM block labeling, so only a single if-else per function definition is possible
* Local and Global variables AST: The problem lies with global variables. A lack of semantic checks means non-literal/constant expressions can be assigned to a global variable in global scope.
* Local and Global variables LLVM: LLVM code for global variables is not entirely correct. Assignments not part of the initialization are possible in global scope.
* Arrays AST: Array declarations are possible, but array literals are not supported, nor is array initialisation. Operations on individual array elements are recognized by the grammar, but no LLVM can be generated for them.