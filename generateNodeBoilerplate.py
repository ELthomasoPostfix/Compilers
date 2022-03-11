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
        for lineIdx in range(len(lines)):
            if lineIdx < len(lines) - 1:
                nxtLine = lines[lineIdx+1]
                matched = match('[ \t]*:', nxtLine)
                if matched is not None and len(matched.group()):
                    varName = match('.*', lines[lineIdx]).group()
                    if varName[0].islower(): grammarVars.append(varName)
        return grammarVars


if __name__ == '__main__':
    srcDir = "Input"
    dstDir = "Output"
    grammarVars = findColonPrefixes(f"{srcDir}/MyGrammar.g4")
    for idx, grammarVar in enumerate(grammarVars):
        grammarVars[idx] = grammarVar[0].upper() + grammarVar[1:]

    with open(f"{dstDir}/nodeBoilerplate.txt", 'w') as of:
        of.write("###############\n# Node forward declarations (ASTreeVisitor.py)\n###############\n")
        for grammarVar in grammarVars:
            of.writelines([f"class {grammarVar}Node:\n\tpass\n"])

        of.writelines(["\n\n\n"])

        of.write("###############\n# Visitor forward declaration (ASTreeVisitor.py)\n###############\n")
        of.write("class ASTreeVisitor:\n")
        for grammarVar in grammarVars:
            of.writelines([f"\tdef visit{grammarVar}(self, value: {grammarVar}Node):\n\t\tpass\n\n"])

        of.writelines(["\n\n\n"])

        of.write("###############\n# Class definitions (ASTreeNode.py)\n###############\n")
        for grammarVar in grammarVars:
            of.writelines([f"class {grammarVar}Node(ASTree):\n\tdef accept(self, visitor: ASTreeVisitor):\n\t\tvisitor.visit{grammarVar}Node(self)\n\n\n"])
