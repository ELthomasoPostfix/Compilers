from antlr4 import *

from src.CompilersUtils import coloredDef
from src.generated.MyGrammarParser import MyGrammarParser
from src.generated.MyGrammarLexer import MyGrammarLexer
from src.generated.MyGrammarListener import MyGrammarListener
from src.ASTree.ASTree import ASTree
from src.ASTreeListener import ASTreeListener
from src.Visitor.OptimizationVisitor import OptimizationVisitor


class KeyPrinter(MyGrammarListener):
    def enterExpression(self, ctx:MyGrammarParser.ExpressionContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (EXP)")

    def enterCfile(self, ctx:MyGrammarParser.CfileContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (CF)")

    def enterBlock(self, ctx:MyGrammarParser.BlockContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (B)")

    def enterLiteral(self, ctx:MyGrammarParser.LiteralContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (LIT)")





def main():
    input_stream = FileStream("Input/test.txt")
    lexer: MyGrammarLexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser: MyGrammarParser = MyGrammarParser(stream)
    tree = parser.cfile()

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
