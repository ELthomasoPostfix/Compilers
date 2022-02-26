from generated.Input.MyGrammarListener import MyGrammarListener
from generated.Input.MyGrammarParser import MyGrammarParser
from ASTree import ASTree


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root = root
        self.current = self.root

    # Enter a parse tree produced by MyGrammarParser#exp.
    def enterExp(self, ctx: MyGrammarParser.ExpContext):
        node = ASTree(None, "EXPRESSION")
        self.root.children.append(node)

    def enterValueexp(self, ctx: MyGrammarParser.ValueexpContext):


    def enterBop(self, ctx: MyGrammarParser.BopContext):
        pass

    def enterValue(self, ctx:MyGrammarParser.ValueContext):
        pass
