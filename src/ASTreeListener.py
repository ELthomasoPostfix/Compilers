from antlr4 import ParserRuleContext

from generated.Input.MyGrammarListener import MyGrammarListener
from generated.Input.MyGrammarParser import MyGrammarParser
from ASTree import ASTree


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root: ASTree = root
        self.current: ASTree = self.root
        self.trace: [ASTree] = []

    def enter(self, node):
        self.current = node
        self.trace.append(node)

    def exit(self):
        self.current = self.trace.pop(-1)

    def enterExp(self, ctx: MyGrammarParser.ExpContext):
        node = ASTree(None, "EXPR")
        self.current.children.append(node)
        self.enter(node)

    def enterValueexp(self, ctx: MyGrammarParser.ValueexpContext):
        node = ASTree(None, "VALUE_EXPR")
        self.current.children.append(node)
        self.enter(node)

    def enterBop(self, ctx: MyGrammarParser.BopContext):
        node = ASTree(ctx.getText(), "BOP")
        self.current.children.append(node)
        self.enter(node)

    def enterValue(self, ctx: MyGrammarParser.ValueContext):
        node = ASTree(ctx.getText(), "VALUE")
        self.current.children.append(node)
        self.enter(node)

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.exit()
