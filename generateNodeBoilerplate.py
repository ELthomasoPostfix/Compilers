#
# Generate node boilerplate code from the specified .g4 file.
# We recognize grammar variables as those strings of alpha characters
# that are followed first by a combination of spaces (' '), tabs ('\t')
# and a single optional newline ('\n') and then by a semicolon (':').
#   e.g.  varName\t \t\n \t\t:
#      or varName2:
#

NODE = "Node"

def findColonPrefixes(filePath: str):
    with open(filePath, "r") as f:
        grammarVars = []
        lines = f.readlines()
        from re import match

        regex = "([a-z_][a-zA-Z_]*)[ \t]*\n?[ \t]*:"
        for idx in range(len(lines) - 1):
            line = lines[idx] + lines[idx+1]
            matched = match(regex, line)
            if matched is not None:
                grammarVars.append(matched.groups()[0])

        return grammarVars


def writeNodeForwardDeclarations(grammarVars, indent: str):
    of.write("###############\n# Node forward declarations (ASTreeVisitor.py)\n###############\n")
    for grammarVar in grammarVars:
        of.writelines([f"class {grammarVar}{NODE}:\n{indent}pass\n"])


def writeVisitorForwardDeclaration(grammarVars, indent: str):
    of.write("###############\n# Visitor forward declaration (ASTreeVisitor.py)\n###############\n")
    of.write("class ASTreeVisitor:\n")
    for grammarVar in grammarVars:
        of.writelines([f"{indent}def visit{grammarVar}(self, value: {grammarVar}Node):\n{indent*2}pass\n\n"])


def writeNodeDefinitions(grammarVars, indent: str):
    of.write("###############\n# Class definitions (ASTreeNode.py)\n###############\n")
    for grammarVar in grammarVars:
        of.writelines([f"class {grammarVar}{NODE}(ASTree):\n{indent}def accept(self, visitor: ASTreeVisitor):\n{indent*2}visitor.visit{grammarVar}(self)\n\n\n"])


def writeListenerDefinition(grammarVars, indent: str, writeText: bool):
    of.write("###############\n# Listener definition (ASTreeListener.py)\n###############\n")
    of.writelines([
        "class ASTreeListener(MyGrammarListener):\n",
            f"{indent}def __init__(self, root):\n",
                f"{indent*2}self.root: ASTree = root\n",
                f"{indent*2}self.current: ASTree = self.root\n",
                f"{indent*2}self.trace: [ASTree] = []\n",
        "\n",
        f"{indent}def enter(self, node):\n",
        f"{indent*2}self.current.children.append(node)\n",
        "\n",
        f"{indent*2}self.current = node\n",
        f"{indent*2}self.trace.append(node)\n",
        "\n",
        f"{indent}def exit(self):\n",
        f"{indent*2}self.trace.pop(-1)\n",
        f"{indent*2}self.current = None if len(self.trace) == 0 else self.trace[-1]\n",
        "\n",
        f"{indent}def exitEveryRule(self, ctx: ParserRuleContext):\n",
        f"{indent*2}self.exit()\n",
        "\n"
    ])
    for grammarVar in grammarVars:
        of.writelines([
            f"{indent}def enter{grammarVar}(self, ctx: MyGrammarParser.{grammarVar}Context):\n",
            f"{indent*2}self.enter({grammarVar}{NODE}({'ctx.getText()' if writeText else 'None'}, \"{grammarVar[:2]}\"))\n",
            "\n"
        ])


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
        of.writelines(["\n\n\n"])

        writeListenerDefinition(grammarVars, indent, True)
