from antlr4 import ParserRuleContext

from generated.Input.MyGrammarListener import MyGrammarListener
from generated.Input.MyGrammarParser import MyGrammarParser
from ASTree import ASTree


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root: ASTree = root
        self.current: ASTree = self.root
        self.trace: [ASTree] = []
        self.ctr = 0

    def enter(self, node):
        self.current = node
        self.trace.append(node)

    def exit(self):
        self.trace.pop(-1)
        self.current = None if len(self.trace) == 0 else self.trace[-1]

    def DOT_PREFIX(self):
        s = str(self.ctr) + "|"
        self.ctr += 1
        return s

    def enterExp(self, ctx: MyGrammarParser.ExpContext):
        node = ASTree(None, self.DOT_PREFIX() + "EXPR")
        self.current.children.append(node)
        self.enter(node)

    def enterValueexp(self, ctx: MyGrammarParser.ValueexpContext):
        node = ASTree(None, self.DOT_PREFIX() + "VALUE_EXPR")
        self.current.children.append(node)
        self.enter(node)

    def enterBop(self, ctx: MyGrammarParser.BopContext):
        node = ASTree(ctx.getText(), self.DOT_PREFIX() + "BOP")
        self.current.children.append(node)
        self.enter(node)

    def enterValue(self, ctx: MyGrammarParser.ValueContext):
        node = ASTree(ctx.getText(), self.DOT_PREFIX() + "VALUE")
        self.current.children.append(node)
        self.enter(node)

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.exit()
