import sys
from antlr4 import *
from generated.Input.MyGrammarParser import MyGrammarParser
from generated.Input.MyGrammarLexer import MyGrammarLexer
from generated.Input.MyGrammarListener import MyGrammarListener
from generated.Input.MyGrammarVisitor import MyGrammarVisitor


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def coloredDef(text):
    return colored(255, 0, 0, text)


class KeyPrinter(MyGrammarListener):
    def exitExp(self, ctx):
        print(f"Werner found a {coloredDef(ctx.getText())} (EXP)")

    def exitValueexp(self, ctx: MyGrammarParser.ValueexpContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (VEXP)")

    def exitBop(self, ctx: MyGrammarParser.BopContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (BOP)")

    def exitValue(self, ctx:MyGrammarParser.ValueContext):
        print(f"Werner found a {coloredDef(ctx.getText())} (VAL)")



def main():
    input_stream = FileStream("../Input/test.txt")
    lexer: MyGrammarLexer = MyGrammarLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser: MyGrammarParser = MyGrammarParser(stream)
    tree = parser.exp()

    # print(tree.toStringTree())
    printer = KeyPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)


if __name__ == '__main__':
    main()