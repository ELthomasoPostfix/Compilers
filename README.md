# Compilers
A project for the course Compilers at the University of Antwerp during the second semester of academic year of 2021-2022. The group is composed of Jeff Boermans and Thomas Gueutal.

# Scripts
All bash (.sh) scripts needed are found in ```Compilers/``` directory. All scripts can be called with the -h flag to display a help message.
Scripts should be called from the /Compilers directory, as they are dependent the compiler file structure.

<b>build.sh</b>: can be called independently to (re)generate the dependency ANTLR python files. Possibly gets called by <b>run.sh</b>.

<b>run.sh</b>:  Treat all positional arguments as to compile files containing C code. Can be called to in one step generate the dependency ANTLR python files, if they do not exist yet, as well as call the main.py file.
The script depends on the <b>build.sh</b> script to generate the dependency ANTLR python files.

Example calls of the compiler follows:
```
./run Input/tests/functions.txt
./run Input/tests/*.txt
./run -h
```
Please note that the <b>run.sh</b> script should be called from the directory it is located in.
The file extension is not checked, so any file may be passed.

# Test files
Example test files are found in the directory ```Compilers/Input/tests2/```. The file names should be
relatively indicative of what they contain and test

# Output
Currently, for a given file ```<input-file>.ext```, with file name ```<input-file>``` and file extension ```ext``` the
compiler will output two .dot files and one .ll file into the output directory ```Compilers/Output/```. The first .dot file is ```beginTree_<file-name>.dot``` and is the AST pre-optimization.
The second .dot file is ```endTree_<file-name>.dot``` and is the AST post-optimization (i.e. literal folding, constant propagation).
The .ll file contains the generated LLVM code for the given input file.

# ANTLR runtime
The ANTLR 4 runtime .jar is provided together with this repository. It is found in the directory ```Compiler/Input/```,
as is the ANTLR grammar file ```MyGrammar.g4```.
As such, all scripts refer to that .jar file instead of any pre-installed versions of ANTLR.

# Features

The design of this table was adopted from the one provided for the course <em>Computer Graphics</em> taught by professor Benny Van Houdt.

---

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
|     | Types pointers             | -                      | X           |             | M    |                                                                                                                 |
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
|     | Printf                     | V                      | X           | -           | M    | Only recognition in input C code                                                                                |
| 4   | Loops                      | V                      | V           |             | M    | for, while                                                                                                      |
|     | Conditionals 1             | V                      | V           |             | M    | if, else                                                                                                        |
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
* Types Pointers: The grammar does not allow (*var)++ or ++(*var). The grammar variable lvalue is missing a similar to 'STAR lvalue' for this to work.
* Semantic Errors: missing operations of incompatible types, assignment to an rvalue and assignment to const variable
* Conditionals 1 LLVM: Unfinished LLVM block labeling, so only a single if-else per function definition is possible
* Local and Global variables AST: The problem lies with global variables. A lack of semantic checks means non-literal/constant expressions can be assigned to a global variable in global scope.
* Local and Global variables LLVM: LLVM code for global variables is not entirely correct. Assignments not part of the initialization are possible in global scope.
* Arrays AST: Array declarations are possible, but array literals are not supported, nor is array initialisation. Operations on individual array elements are recognized by the grammar, but no LLVM can be generated for them.