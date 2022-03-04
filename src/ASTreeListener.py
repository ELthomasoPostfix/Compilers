from antlr4 import ParserRuleContext

from generated.Input.MyGrammarListener import MyGrammarListener
from generated.Input.MyGrammarParser import MyGrammarParser
from src.Nodes.ASTreeNode import *


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root: ASTree = root
        self.current: ASTree = self.root
        self.trace: [ASTree] = []

    def enter(self, node):
        self.current = node
        self.trace.append(node)

    def exit(self):
        self.trace.pop(-1)
        self.current = None if len(self.trace) == 0 else self.trace[-1]

    def enterExp(self, ctx: MyGrammarParser.ExpContext):
        node = ExpNode(None, "EXPR")
        self.current.children.append(node)
        self.enter(node)

    def enterValueexp(self, ctx: MyGrammarParser.ValueexpContext):
        node = ValueExpNode(None, "VALUE_EXPR")
        self.current.children.append(node)
        self.enter(node)

    def exitValueexp(self, ctx: MyGrammarParser.ValueexpContext):
        valExp = self.trace[-1]
        if len(valExp.children) == 1 and isinstance(valExp.children[0], ValueNode):
            val: ValueNode = valExp.children[0]
            valExp.children.clear()

            parent: ASTree = self.trace[-2]
            parent.children[parent.children.index(valExp)] = val

        elif len(valExp.children) == 3 and isinstance(valExp.children[1], BopNode):
            bop: BopNode = valExp.children[1]
            bop.children.append(valExp.children[0])
            bop.children.append(valExp.children[2])
            valExp.children.clear()

            parent: ASTree = self.trace[-2]
            parent.children[parent.children.index(valExp)] = bop

    def enterBop(self, ctx: MyGrammarParser.BopContext):
        node = BopNode(ctx.getText(), "BOP")
        self.current.children.append(node)
        self.enter(node)

    def enterValue(self, ctx: MyGrammarParser.ValueContext):
        node = ValueNode(ctx.getText(), "VALUE")
        self.current.children.append(node)
        self.enter(node)

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.exit()
