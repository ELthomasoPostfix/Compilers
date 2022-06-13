import re
import sys

from antlr4 import *

from src.CompilersUtils import coloredDef, ftoi, ctoi, toCaptureRange
from src.Enumerations import BuiltinNames, MIPSLocation
from src.Exceptions.exceptions import CCompilerException
from src.Nodes.LiteralNodes import IntegerNode, CharNode
from src.SymbolTable import TypeList
from src.Visitor.MIPSVisitor import MIPSVisitor
from src.Visitor.SemanticVisitor import SemanticVisitor
from src.Visitor.SymbolVisitor import SymbolVisitor
from src.generated.MyGrammarParser import MyGrammarParser
from src.generated.MyGrammarLexer import MyGrammarLexer
from src.generated.MyGrammarListener import MyGrammarListener
from src.ASTreeListener import ASTreeListener
from src.Visitor.OptimizationVisitor import OptimizationVisitor
from src.Visitor.LLVMVisitor import LLVMVisitor


def main():
    try:
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

        outputType = "c"

        # llvmVisitor = LLVMVisitor(tl)
        # listener.root.accept(llvmVisitor)
        # a = llvmVisitor.instructions
        # outputType = "ll"

        mipsVisitor = MIPSVisitor(tl)
        listener.root.accept(mipsVisitor)
        a = mipsVisitor.instructions
        outputType = "asm"

        file = open("Output/" + f"{ifName}.{outputType}", "w")
        for string in a:
            file.write(string)

        print(tree.getText())
        print()

    except CCompilerException as ex_name:
        print(coloredDef(ex_name.printmsg))

if __name__ == '__main__':
    main()
