from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from src.generated.MyGrammarListener import MyGrammarListener
from src.generated.MyGrammarParser import MyGrammarParser
from src.Nodes.OperatorNodes import *
from src.Nodes.LiteralNodes import *


class ASTreeListener(MyGrammarListener):
    def __init__(self):
        self.root: ASTree = None
        self.current: ASTree = self.root

        self.pushDepths = []
        self.cstDepth = 0

    def addCurrentChild(self, node):
        if self.current is None:
            self.root = node
        else:
            self.current.children.append(node)

        node.parent = self.current

        self.current = node
        self.pushDepths.append(self.cstDepth)

    def enterEveryRule(self, ctx:ParserRuleContext):
        self.cstDepth += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        if self.cstDepth == self.pushDepths[-1]:
            self.pushDepths.pop(-1)
            self.current = self.current.parent
        self.cstDepth -= 1

    def enterCfile(self, ctx: MyGrammarParser.CfileContext):
        self.addCurrentChild(CfileNode(ctx.getText(), "Cf"))

    def enterBlock(self, ctx: MyGrammarParser.BlockContext):
        self.addCurrentChild(BlockNode(ctx.getText(), "Bl"))

    def enterStatement(self, ctx: MyGrammarParser.StatementContext):
        self.addCurrentChild(StatementNode(ctx.getText(), "St"))

    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        if isinstance(ctx.children[0], MyGrammarParser.LiteralContext) or \
                self.isTerminalType(ctx.children[0], MyGrammarParser.LPAREN):
            return
        else:
            self.addCurrentChild(ExpressionNode(ctx.getText(), "Ex"))



    def enterUnaryexpression(self, ctx: MyGrammarParser.UnaryexpressionContext):
        self.addCurrentChild(UnaryexpressionNode(ctx.getText(), "Un"))

    def enterAddexp(self, ctx:MyGrammarParser.AddexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.PLUS):
            self.addCurrentChild(SumNode(ctx.getText(), "SUM"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MIN):
            self.addCurrentChild(MinNode(ctx.getText(), "MIN"))

    def enterMultiplicationexp(self, ctx:MyGrammarParser.MultiplicationexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.STAR):
            self.addCurrentChild(MulNode(ctx.getText(), "MUL"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.DIV):
            self.addCurrentChild(DivNode(ctx.getText(), "DIV"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MOD):
            self.addCurrentChild(ModNode(ctx.getText(), "MOD"))


    def enterEqualityexp(self, ctx:MyGrammarParser.EqualityexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.EQ):
            self.addCurrentChild(EqNode(ctx.getText(), "EQ"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.NEQ):
            self.addCurrentChild(NeqNode(ctx.getText(), "NEQ"))

    def enterRelationalexp(self, ctx:MyGrammarParser.RelationalexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.LT):
            self.addCurrentChild(LtNode(ctx.getText(), "LT"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.LTE):
            self.addCurrentChild(LteNode(ctx.getText(), "LTE"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GT):
            self.addCurrentChild(GtNode(ctx.getText(), "GT"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GTE):
            self.addCurrentChild(GteNode(ctx.getText(), "GTE"))

    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        # TODO collapse a series of unary operators (or do this in optimisation?)
        self.addCurrentChild(UnaryopNode(ctx.getText(), "Un"))

    def enterLiteral(self, ctx: MyGrammarParser.LiteralContext):
        if self.isTerminalType(ctx.getChild(0), MyGrammarParser.INT):
            self.addCurrentChild(IntegerNode(ctx.getText(), "In"))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.FLOAT):
            self.addCurrentChild(FloatNode(ctx.getText(), "Fl"))

    def enterVar(self, ctx: MyGrammarParser.VarContext):
        self.addCurrentChild(VarNode(ctx.getText(), "Va"))

    def enterC_type(self, ctx: MyGrammarParser.C_typeContext):
        self.addCurrentChild(C_typeNode(ctx.getText(), "C_"))

    def enterQualifier(self, ctx: MyGrammarParser.QualifierContext):
        self.addCurrentChild(QualifierNode(ctx.getText(), "Qu"))

    def enterVar_decl(self, ctx: MyGrammarParser.Var_declContext):
        self.addCurrentChild(Var_declNode(ctx.getText(), "Va"))

    def enterVar_assig(self, ctx: MyGrammarParser.Var_assigContext):
        self.addCurrentChild(Var_assigNode(ctx.getText(), "Va"))


    def isTerminalType(self, node: ParserRuleContext, terminalID: int):
        return isinstance(node, TerminalNodeImpl) and node.symbol.type == terminalID

