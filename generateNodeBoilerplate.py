#
# Generate node boilerplate code from the specified .g4 file.
# We recognize grammar variables as those strings of alpha characters
# that are followed first by a combination of spaces (' '), tabs ('\t')
# and a single optional newline ('\n') and then by a semicolon (':').
#   e.g.  varName\t \t\n \t\t:
#      or varName2:
#
import os.path
import sys

from src.CompilersUtils import FlagContainer

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


def reduceToImports(ofile):
    imports = readImports(ofile)
    ofile.seek(0)
    ofile.truncate()

    ASTreeNode.writelines(imports)
    ASTreeNode.writelines(["\n\n\n"])


def writeNodeForwardDeclarations(ofile, grammarVars, indent: str):
    ofile.write(f"class ASTree:\n")
    ofile.write(f"{indent}def __init__(self):\n")
    ofile.write(f"{indent*2}self.children = None\n")

    ofile.write("\n\n")

    for grammarVar in grammarVars:
        ofile.writelines([f"class {grammarVar}{NODE}:\n{indent}pass\n"])


def writeVisitorForwardDeclaration(ofile, grammarVars, indent: str):
    ofile.write("class ASTreeVisitor:\n")

    ofile.write(f"{indent}def visitChildren(self, node: ASTree):\n")
    ofile.write(f"{indent*2}for c in node.children:\n")
    ofile.write(f"{indent*3}c.accept(self)\n\n")

    ofile.write(f"{indent}def visitBinaryop(self, node: ASTree):\n")
    ofile.write(f"{indent*2}self.visitChildren(node)\n\n")

    ofile.write("\n\n")

    for grammarVar in grammarVars:
        ofile.writelines([f"{indent}def visit{grammarVar}(self, node: {grammarVar}Node):\n{indent*2}self.visitChildren(node)\n\n"])


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



    grammarFile = "Input/MyGrammar.g4"
    nodesFile = "src/Nodes/ASTreeNode.py"
    visitorFile = "src/Visitor/ASTreeVisitor.py"
    boilerplateFile = "Output/nodeBoilerplate.txt"
    fc = FlagContainer()

    try:

        fc.registerFlagType("help", {"-h", "--help"})
        fc.registerExplanation("help", "Display this help message")

        if FlagContainer.argc() == 1:
            print("No arguments passed, try calling with the following flags for help:", fc.flags["help"])
            exit(0)

        fc.registerFlagType("all", {"-a", "--all"})
        fc.registerExplanation("all", "Generate all files")
        fc.registerFlagType("nodes", {"-n", "--nodes"})
        fc.registerExplanation("nodes", f"Generate Node class definitions (output file: {nodesFile})")
        fc.registerFlagType("visitor", {"-v", "--visitor"})
        fc.registerExplanation("visitor", f"Generate Node class forward declarations and visitor class declaration (output file: {visitorFile})")
        fc.registerFlagType("boilerplate", {"-b", "--boilerplate"})
        fc.registerExplanation("boilerplate", f"Generate Listener class boilerplate (output file: {boilerplateFile})")
        fc.registerFlagType("force", {"-F", "--force"})
        fc.registerExplanation("force", "A safety flag that may be required in combination with other flags to ensure critical files are not accidentally overwritten")
    except Exception as e:
        print(e)
        exit(0)

    if fc.checkFlag("help"):
        print("The following files may be affected:")
        for filePath in [grammarFile, nodesFile, visitorFile, boilerplateFile]:
            print(f"\t{filePath}")
        print("The following flags are supported:")
        for key in fc.flags.keys():
            print(f"{fc.flags[key]}   :\t   {fc.getExplanation(key)}")
    else:
        indent = ' ' * 4
        grammarVars = findColonPrefixes(grammarFile)
        for idx, grammarVar in enumerate(grammarVars):
            grammarVars[idx] = grammarVar[0].upper() + grammarVar[1:]

        if (fc.checkFlag("nodes") or fc.checkFlag("all")) and os.path.exists(nodesFile):
            if False:
                if fc.checkFlag("force"):
                    with open(nodesFile, 'r+') as ASTreeNode:
                        reduceToImports(ASTreeNode)

                        writeNodeDefinitions(ASTreeNode, grammarVars, indent)
                        ASTreeNode.writelines(["\n\n\n"])
                else:
                    print(f"Missing {fc.flags['force']} flag!")
            else:
                print("ASTreeNode.py has too many manual modifications for autogeneration to be worth it rn.")

        if (fc.checkFlag("visitor") or fc.checkFlag("all")) and os.path.exists(visitorFile):
            with open(visitorFile, 'r+') as ASTreeVisitor:
                ASTreeVisitor.seek(0)
                ASTreeVisitor.truncate()

                writeNodeForwardDeclarations(ASTreeVisitor, grammarVars, indent)
                ASTreeVisitor.writelines(["\n\n\n"])

                writeVisitorForwardDeclaration(ASTreeVisitor, grammarVars, indent)

        if fc.checkFlag("boilerplate") or fc.checkFlag("all"):
            with open(boilerplateFile, 'w') as ASTreeListener:
                writeListenerDefinition(ASTreeListener, grammarVars, indent, True)
