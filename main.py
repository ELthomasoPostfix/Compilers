import sys
from ctypes import sizeof

from antlr4 import *

from src.CompilersUtils import coloredDef
from src.Nodes.ASTreeNode import CompoundstatementNode
from src.SymbolTable import SymbolTable, ReadAccess, ReadWriteAccess, Accessibility, TypeList, Record
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

    printer = KeyPrinter()
    listener = ASTreeListener()  # TODO make the root of the CST var 'tree' the ASTree root instead
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    walker.walk(listener, tree)
    listener.root.toDot("beginTree.dot")

    OVisitor = OptimizationVisitor()
    llvmVisitor = LLVMVisitor()
    tl = TypeList(["char", "int", "float"])
    SVisitor = SymbolVisitor(SymbolTable(None, tl))
    listener.root.accept(OVisitor)
    listener.root.accept(llvmVisitor)
    listener.root.accept(SVisitor)

    listener.root.toDot("endTree.dot", detailed=True)

    print(tree.getText())

    # TODO  garbage
    # TODO  garbage
    # TODO  garbage
    r = ReadAccess()
    r1 = ReadAccess()
    rw = ReadWriteAccess()
    rw1 = ReadWriteAccess()
    i: int = 2
    print(r)
    print(rw)
    print("r == r", r == r1)
    print("rw == rw", rw1 == rw)
    print("r == rw", r == rw)
    print(r.__sizeof__())
    print(i.__sizeof__())

    print(tl["char"])
    print(tl[1])
    tl.append("short")
    st = SymbolTable(None, tl)
    st["id1"] = Record(0, ReadAccess())
    st["id3"] = Record(2, ReadWriteAccess())

    print(st)
    # TODO  garbage
    # TODO  garbage
    # TODO  garbage


if __name__ == '__main__':
    main()
