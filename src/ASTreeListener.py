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

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.exit()

    def enterCfile(self, ctx: MyGrammarParser.CfileContext):
        self.enter(CfileNode(ctx.getText(), "Cf"))

    def enterBlock(self, ctx: MyGrammarParser.BlockContext):
        self.enter(BlockNode(ctx.getText(), "Bl"))

    def enterStatement(self, ctx: MyGrammarParser.StatementContext):
        self.enter(StatementNode(ctx.getText(), "St"))

    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        self.enter(ExpressionNode(ctx.getText(), "Ex"))

    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        self.enter(UnaryopNode(ctx.getText(), "Un"))

    def enterRelationalop(self, ctx: MyGrammarParser.RelationalopContext):
        self.enter(RelationalopNode(ctx.getText(), "Re"))

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
