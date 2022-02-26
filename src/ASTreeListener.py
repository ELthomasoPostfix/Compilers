from generated.Input.MyGrammarListener import MyGrammarListener
from generated.Input.MyGrammarParser import MyGrammarParser
from ASTree import ASTree


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root = root
        self.current = self.root

    # Enter a parse tree produced by MyGrammarParser#exp.
    def enterExp(self, ctx: MyGrammarParser.ExpContext):
        # EXPRESSION
        expNode = ASTree(None, "EXPRESSION")
        self.root.children.append(expNode)

    def exitValueexp(self, ctx: MyGrammarParser.ValueexpContext):


    def exitBop(self, ctx: MyGrammarParser.BopContext):
        pass

    def exitValue(self, ctx:MyGrammarParser.ValueContext):
        pass
