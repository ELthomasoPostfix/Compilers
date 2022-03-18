from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from src.generated.MyGrammarListener import MyGrammarListener
from src.generated.MyGrammarParser import MyGrammarParser
from src.Nodes.ASTreeNode import *
from src.Nodes.DerivedASTreeNodes import *


class ASTreeListener(MyGrammarListener):
    def __init__(self, root):
        self.root: ASTree = root
        self.current: ASTree = self.root
        self.trace: [ASTree] = []
        self.pushDepths = []
        self.cstDepth = 0

    def enter(self, node):
        self.current.children.append(node)
        node.parent = self.current

        self.current = node
        self.pushDepths.append(self.cstDepth)
        self.trace.append(node)

    def enterEveryRule(self, ctx:ParserRuleContext):
        self.cstDepth += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        if self.cstDepth == self.pushDepths[-1]:
            self.pushDepths.pop(-1)
            self.trace.pop(-1)
            self.current = self.trace[-1] if len(self.trace) > 0 else None
        self.cstDepth -= 1

    def enterCfile(self, ctx: MyGrammarParser.CfileContext):
        self.enter(CfileNode(ctx.getText(), "Cf"))

    def enterBlock(self, ctx: MyGrammarParser.BlockContext):
        self.enter(BlockNode(ctx.getText(), "Bl"))

    def enterStatement(self, ctx: MyGrammarParser.StatementContext):
        self.enter(StatementNode(ctx.getText(), "St"))

    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        if isinstance(ctx.children[0], MyGrammarParser.LiteralContext) or \
                self.isTerminalType(ctx.children[0], MyGrammarParser.LPAREN):
            return
        else:
            self.enter(ExpressionNode(ctx.getText(), "Ex"))



    def enterUnaryexpression(self, ctx: MyGrammarParser.UnaryexpressionContext):
        self.enter(UnaryexpressionNode(ctx.getText(), "Un"))

    def enterAddexp(self, ctx:MyGrammarParser.AddexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.PLUS):
            self.enter(SumNode(ctx.getText(), "SUM"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MIN):
            self.enter(MinNode(ctx.getText(), "MIN"))

    def enterMultiplicationexp(self, ctx:MyGrammarParser.MultiplicationexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.STAR):
            self.enter(MulNode(ctx.getText(), "MUL"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.DIV):
            self.enter(DivNode(ctx.getText(), "DIV"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MOD):
            self.enter(ModNode(ctx.getText(), "MOD"))


    def enterEqualityexp(self, ctx:MyGrammarParser.EqualityexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.EQ):
            self.enter(EqNode(ctx.getText(), "EQ"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.NEQ):
            self.enter(NeqNode(ctx.getText(), "NEQ"))

    def enterParenthesisexp(self, ctx:MyGrammarParser.ParenthesisexpContext):
        pass

    def enterRelationalexp(self, ctx:MyGrammarParser.RelationalexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.LT):
            self.enter(LtNode(ctx.getText(), "LT"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.LTE):
            self.enter(LteNode(ctx.getText(), "LTE"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GT):
            self.enter(GtNode(ctx.getText(), "GT"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GTE):
            self.enter(GteNode(ctx.getText(), "GTE"))


    def enterUnaryexp(self, ctx:MyGrammarParser.UnaryexpContext):
        pass


    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        # TODO collapse a series of unary operators (or do this in optimisation?)
        self.enter(UnaryopNode(ctx.getText(), "Un"))

    def enterLiteral(self, ctx: MyGrammarParser.LiteralContext):
        self.enter(LiteralNode(ctx.getText(), "Li"))

    def enterLval(self, ctx: MyGrammarParser.LvalContext):
        self.enter(LvalNode(ctx.getText(), "Lv"))

    def enterC_type(self, ctx: MyGrammarParser.C_typeContext):
        self.enter(C_typeNode(ctx.getText(), "C_"))

    def enterQualifier(self, ctx: MyGrammarParser.QualifierContext):
        self.enter(QualifierNode(ctx.getText(), "Qu"))

    def enterVar_decl(self, ctx: MyGrammarParser.Var_declContext):
        self.enter(Var_declNode(ctx.getText(), "Va"))

    def enterVar_assig(self, ctx: MyGrammarParser.Var_assigContext):
        self.enter(Var_assigNode(ctx.getText(), "Va"))



    def isTerminalType(self, node: ParserRuleContext, terminalID: int):
        return isinstance(node, TerminalNodeImpl) and node.symbol.type == terminalID

