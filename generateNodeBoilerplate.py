#
# Generate node boilerplate code from the specified .g4 file.
# We recognize grammar variables as those strings of alpha characters
# that are followed first by a combination of spaces (' '), tabs ('\t')
# and a single optional newline ('\n') and then by a semicolon (':').
#   e.g.  varName\t \t\n \t\t:
#      or varName2:
#
import os.path

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


def readImports(ofile):
    imports = []
    for line in ofile.readlines():
        if "import " in line or "from " in line:
            imports.append(line)
    return imports


def writeNodeForwardDeclarations(ofile, grammarVars, indent: str):
    for grammarVar in grammarVars:
        ofile.writelines([f"class {grammarVar}{NODE}:\n{indent}pass\n"])


def writeVisitorForwardDeclaration(ofile, grammarVars, indent: str):
    ofile.write("class ASTreeVisitor:\n")
    for grammarVar in grammarVars:
        ofile.writelines([f"{indent}def visit{grammarVar}(self, value: {grammarVar}Node):\n{indent*2}pass\n\n"])


def writeNodeDefinitions(ofile, grammarVars, indent: str):
    for grammarVar in grammarVars:
        ofile.writelines([f"class {grammarVar}{NODE}(ASTree):\n{indent}def accept(self, visitor: ASTreeVisitor):\n{indent*2}visitor.visit{grammarVar}(self)\n\n\n"])


def writeListenerDefinition(ofile, grammarVars, indent: str, writeText: bool):
    ofile.write("###############\n# Listener definition (ASTreeListener.py)\n###############\n")
    ofile.writelines([
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
        ofile.writelines([
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

    if os.path.exists("src/Nodes/ASTreeNode.py"):
        with open(f"src/Nodes/ASTreeNode.py", 'r+') as ASTreeNode:
            imports = readImports(ASTreeNode)
            ASTreeNode.seek(0)
            ASTreeNode.truncate()

            ASTreeNode.writelines(imports)
            ASTreeNode.writelines(["\n\n\n"])

            writeNodeDefinitions(ASTreeNode, grammarVars, indent)
            ASTreeNode.writelines(["\n\n\n"])

    if os.path.exists("src/Visitor/ASTreeVisitor.py"):
        with open(f"src/Visitor/ASTreeVisitor.py", 'r+') as ASTreeVisitor:
            ASTreeVisitor.seek(0)
            ASTreeVisitor.truncate()

            writeNodeForwardDeclarations(ASTreeVisitor, grammarVars, indent)
            ASTreeVisitor.writelines(["\n\n\n"])

            writeVisitorForwardDeclaration(ASTreeVisitor, grammarVars, indent)

    with open(f"{dstDir}/nodeBoilerplate.txt", 'w') as ASTreeListener:
        writeListenerDefinition(ASTreeListener, grammarVars, indent, True)
