import sys

from antlr4 import *

from src.CompilersUtils import coloredDef
from src.Enumerations import BuiltinNames
from src.SymbolTable import TypeList
from src.Visitor.SemanticVisitor import SemanticVisitor
from src.Visitor.SymbolVisitor import SymbolVisitor
from src.generated.MyGrammarParser import MyGrammarParser
from src.generated.MyGrammarLexer import MyGrammarLexer
from src.generated.MyGrammarListener import MyGrammarListener
from src.ASTreeListener import ASTreeListener
from src.Visitor.OptimizationVisitor import OptimizationVisitor
from src.Visitor.LLVMVisitor import LLVMVisitor


class KeyPrinter(MyGrammarListener):
    def enterExpression(self, ctx:MyGrammarParser.ExpressionContext):
        print(f"Compiler found a {coloredDef(ctx.getText())} (EXP)")

    def enterCfile(self, ctx:MyGrammarParser.CfileContext):
        print(f"Compiler found a {coloredDef(ctx.getText())} (CF)")

    def enterBlock(self, ctx:MyGrammarParser.BlockContext):
        print(f"Compiler found a {coloredDef(ctx.getText())} (B)")

    def enterLiteral(self, ctx:MyGrammarParser.LiteralContext):
        print(f"Compiler found a {coloredDef(ctx.getText())} (LIT)")





def main():
    ifPath = sys.argv[1]
    ifName = ifPath.split('/')[-1].split('.')[0]

    input_stream = FileStream(ifPath)
    lexer: MyGrammarLexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser: MyGrammarParser = MyGrammarParser(stream)
    tree = parser.cfile()

    tl = TypeList([BuiltinNames.VOID, BuiltinNames.CHAR, BuiltinNames.INT, BuiltinNames.FLOAT])
    listener = ASTreeListener(tl)  # TODO make the root of the CST var 'tree' the ASTree root instead
    walker = ParseTreeWalker()
    walker.walk(listener, tree)



    listener.root.toDot(f"beginTree_{ifName}.dot", detailed=True)

    SVisitor = SymbolVisitor(tl)
    listener.root.accept(SVisitor)

    SemVisitor = SemanticVisitor(tl)
    listener.root.accept(SemVisitor)

    OVisitor = OptimizationVisitor()
    listener.root.accept(OVisitor)

    listener.root.toDot(f"endTree_{ifName}.dot", detailed=True)

    llvmVisitor = LLVMVisitor(tl)
    listener.root.accept(llvmVisitor)
    a = llvmVisitor.instructions

    file = open("Output/" + f"{ifName}.ll", "w")
    for string in a:
        file.write(string)

    print(tree.getText())
    print()


if __name__ == '__main__':
    main()
