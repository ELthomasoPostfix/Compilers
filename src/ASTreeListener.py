from antlr4 import ParserRuleContext

from src.generated.MyGrammarListener import MyGrammarListener
from src.generated.MyGrammarParser import MyGrammarParser
from src.Nodes.ASTreeNode import *


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root: ASTree = root
        self.current: ASTree = self.root
        self.trace: [ASTree] = []

    def enter(self, node):
        self.current.children.append(node)

        self.current = node
        self.trace.append(node)


    def exit(self):
        self.trace.pop(-1)
        self.current = None if len(self.trace) == 0 else self.trace[-1]

    def enterCfile(self, ctx:MyGrammarParser.CfileContext):
        node = (None, "CF")
        self.enter(node)

    def enterBlock(self, ctx:MyGrammarParser.BlockContext):
        node = StatementNode(None, "B")
        self.enter(node)

    def enterStatement(self, ctx:MyGrammarParser.StatementContext):
        node = StatementNode(None, "STAT")
        self.enter(node)

    def enterExpression(self, ctx:MyGrammarParser.ExpressionContext):
        node = ExpressionNode(None, "EXPR")
        self.enter(node)

    def enterRelationalop(self, ctx:MyGrammarParser.RelationalopContext):
        node = RelationalOpNode(ctx.getText(), "ROP")
        self.enter(node)

    def enterValue(self, ctx: MyGrammarParser.ValueContext):
        node = ValueNode(ctx.getText(), "VALUE")
        self.enter(node)

    def enterUnaryop(self, ctx:MyGrammarParser.UnaryopContext):
        node = UnaryOpNode(ctx.getText(), "UOP")
        self.enter(node)

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.exit()
