from antlr4 import *
from generated.MyGrammarParser import MyGrammarParser
from generated.MyGrammarLexer import MyGrammarLexer
from generated.MyGrammarListener import MyGrammarListener
from ASTree.ASTree import ASTree
from ASTreeListener import ASTreeListener
from Visitor.OptimizationVisitor import OptimizationVisitor
from CompilersUtils import coloredDef


class KeyPrinter(MyGrammarListener):
    def enterExp(self, ctx):
        print(f"Werner found a {coloredDef(ctx.getText())} (EXP)")

    def enterValueexp(self, ctx):
        print(f"Werner found a {coloredDef(ctx.getText())} (VEXP)")

    def enterBop(self, ctx):
        print(f"Werner found a {coloredDef(ctx.getText())} (BOP)")

    def enterValue(self, ctx):
        print(f"Werner found a {coloredDef(ctx.getText())} (VAL)")





def main():
    input_stream = FileStream("Input/test.txt")
    lexer: MyGrammarLexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser: MyGrammarParser = MyGrammarParser(stream)
    tree = parser.expression()

    printer = KeyPrinter()
    listener = ASTreeListener(
        ASTree(name="root", value=None))  # TODO make the root of the CST var 'tree' the ASTree root instead
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    walker.walk(listener, tree)
    listener.root.toDot("beginTree.dot")

    OListener = OptimizationVisitor()
    listener.root.children[0].children[0].accept(OListener)

    listener.root.toDot("endTree.dot")

    print(tree.getText())


if __name__ == '__main__':
    main()
