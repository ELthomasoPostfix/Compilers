#
# Generate node boilerplate code from the specified .g4 file.
# We recognize a grammar variable if and only if the following line contains a semicolon (':').
# The name of the variable in the .g4 file should not be followed by any other character, including spaces and comments,
# because the entire line, excluding \n or the like, is considered the variable name.
#

def findColonPrefixes(filePath: str):
    with open(filePath, "r") as f:
        grammarVars = []
        lines = f.readlines()
        from re import match

        regex = "([a-z][a-zA-Z]*)[ \t]*\n?[ \t]*:"
        for idx in range(len(lines) - 1):
            line = lines[idx] + lines[idx+1]
            matched = match(regex, line)
            if matched is not None:
                grammarVars.append(matched.groups()[0])

        return grammarVars


def writeNodeForwardDeclarations(grammarVars, indent: str):
    of.write("###############\n# Node forward declarations (ASTreeVisitor.py)\n###############\n")
    for grammarVar in grammarVars:
        of.writelines([f"class {grammarVar}Node:\n{indent}pass\n"])


def writeVisitorForwardDeclaration(grammarVars, indent: str):
    of.write("###############\n# Visitor forward declaration (ASTreeVisitor.py)\n###############\n")
    of.write("class ASTreeVisitor:\n")
    for grammarVar in grammarVars:
        of.writelines([f"{indent}def visit{grammarVar}(self, value: {grammarVar}Node):\n{indent*2}pass\n\n"])


def writeNodeDefinitions(grammarVars, indent: str):
    of.write("###############\n# Class definitions (ASTreeNode.py)\n###############\n")
    for grammarVar in grammarVars:
        of.writelines([f"class {grammarVar}Node(ASTree):\n{indent}def accept(self, visitor: ASTreeVisitor):\n{indent*2}visitor.visit{grammarVar}(self)\n\n\n"])


if __name__ == '__main__':
    srcDir = "Input"
    dstDir = "Output"
    indent = ' ' * 4
    grammarVars = findColonPrefixes(f"{srcDir}/MyGrammar.g4")
    for idx, grammarVar in enumerate(grammarVars):
        grammarVars[idx] = grammarVar[0].upper() + grammarVar[1:]

    with open(f"{dstDir}/nodeBoilerplate.txt", 'w') as of:
        writeNodeForwardDeclarations(grammarVars, indent)
        of.writelines(["\n\n\n"])

        writeVisitorForwardDeclaration(grammarVars, indent)
        of.writelines(["\n\n\n"])

        writeNodeDefinitions(grammarVars, indent)

