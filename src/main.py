from antlr4 import *
from generated.Input.MyGrammarParser import MyGrammarParser
from generated.Input.MyGrammarLexer import MyGrammarLexer
from generated.Input.MyGrammarListener import MyGrammarListener
from src.ASTree.ASTree import ASTree
from ASTreeListener import ASTreeListener
from src.Visitor.OptimizationVisitor import OptimizationVisitor
from src.CompilersUtils import coloredDef


class KeyPrinter(MyGrammarListener):
    def enterExp(self, ctx):
        print(f"Werner found a {coloredDef(ctx.getText())} (EXP)")

    def enterValueexp(self, ctx: MyGrammarParser.ValueexpContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (VEXP)")

    def enterBop(self, ctx: MyGrammarParser.BopContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (BOP)")

    def enterValue(self, ctx:MyGrammarParser.ValueContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (VAL)")



def main():
    input_stream = FileStream("../Input/test.txt")
    lexer: MyGrammarLexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser: MyGrammarParser = MyGrammarParser(stream)
    tree = parser.exp()

    printer = KeyPrinter()
    listener = ASTreeListener(ASTree(name="root", value=None))    # TODO make the root of the CST var 'tree' the ASTree root instead
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    walker.walk(listener, tree)
    listener.root.toDot()

    OListener = OptimizationVisitor()
    nodes = listener.root.preorderTraverse([], 0)
    for node, layer in nodes:
        node.accept(OListener)



if __name__ == '__main__':
    main()
