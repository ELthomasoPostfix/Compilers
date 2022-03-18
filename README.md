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
