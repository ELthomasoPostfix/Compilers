import sys
from ctypes import sizeof

from antlr4 import *

from src.CompilersUtils import coloredDef
from src.Nodes.ASTreeNode import CompoundstatementNode, TypedNode, IdentifierNode
from src.Nodes.BuiltinInfo import BuiltinNames
from src.SymbolTable import SymbolTable, ReadAccess, ReadWriteAccess, Accessibility, TypeList, Record, CType, \
    VariableCType, FunctionCType
from src.Visitor.SymbolVisitor import SymbolVisitor
from src.generated.MyGrammarParser import MyGrammarParser
from src.generated.MyGrammarLexer import MyGrammarLexer
from src.generated.MyGrammarListener import MyGrammarListener
from src.ASTree.ASTree import ASTree
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
    input_stream = FileStream(sys.argv[1])
    lexer: MyGrammarLexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser: MyGrammarParser = MyGrammarParser(stream)
    tree = parser.cfile()

    listener = ASTreeListener()  # TODO make the root of the CST var 'tree' the ASTree root instead
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    listener.root.toDot("beginTree.dot", detailed=True)

    OVisitor = OptimizationVisitor()
    llvmVisitor = LLVMVisitor()
    tl = TypeList([BuiltinNames.VOID, BuiltinNames.CHAR, BuiltinNames.INT, BuiltinNames.FLOAT])
    SVisitor = SymbolVisitor(SymbolTable(None, tl))
    listener.root.accept(OVisitor)
    listener.root.accept(llvmVisitor)
    listener.root.accept(SVisitor)

    listener.root.toDot("endTree.dot", detailed=True)

    print(tree.getText())
    print()


if __name__ == '__main__':
    main()
