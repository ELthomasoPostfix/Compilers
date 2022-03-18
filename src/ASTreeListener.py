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
        self.skipDepths = []

    def enter(self, node):
        self.current.children.append(node)
        node.parent = self.current

        self.current = node
        self.trace.append(node)

    def shouldSkip(self):
        return len(self.skipDepths) > 0 and len(self.trace) == self.skipDepths[-1]

    def exit(self):
        if self.shouldSkip():   # Prevent exit from executing on skipped nodes
            print("skip", self.skipDepths[-1])
            self.skipDepths.pop(-1)
        else:
            self.trace.pop(-1)
            self.current = None if len(self.trace) == 0 else self.trace[-1]

    def skip(self):
        self.skipDepths.append(len(self.trace))

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.exit()

    def enterCfile(self, ctx: MyGrammarParser.CfileContext):
        self.enter(CfileNode(ctx.getText(), "Cf"))

    def enterBlock(self, ctx: MyGrammarParser.BlockContext):
        self.enter(BlockNode(ctx.getText(), "Bl"))

    def enterStatement(self, ctx: MyGrammarParser.StatementContext):
        self.enter(StatementNode(ctx.getText(), "St"))

    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        if isinstance(ctx.children[0], MyGrammarParser.LiteralContext) or \
                self.isTerminalType(ctx.children[0], MyGrammarParser.LPAREN):
            self.skip()
            return
        else:
            self.enter(ExpressionNode(ctx.getText(), "Ex"))

    def enterUnaryexpression(self, ctx: MyGrammarParser.UnaryexpressionContext):
        self.enter(UnaryexpressionNode(ctx.getText(), "Un"))

    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        # TODO collapse a series of unary operators (or do this in optimisation?)
        self.enter(UnaryopNode(ctx.getText(), "Un"))

    def enterBinaryop(self, ctx: MyGrammarParser.BinaryopContext):
        if self.isTerminalType(ctx.children[0], MyGrammarParser.PLUS):
            self.substituteTraceBottom(SumNode(ctx.getText(), "Sum"))
        elif self.isTerminalType(ctx.children[0], MyGrammarParser.MIN):
            self.substituteTraceBottom(MinNode(ctx.getText(), "Min"))
        elif self.isTerminalType(ctx.children[0], MyGrammarParser.STAR):
            self.substituteTraceBottom(MulNode(ctx.getText(), "Mul"))
        elif self.isTerminalType(ctx.children[0], MyGrammarParser.DIV):
            self.substituteTraceBottom(DivNode(ctx.getText(), "Div"))
        elif self.isTerminalType(ctx.children[0], MyGrammarParser.MOD):
            self.substituteTraceBottom(ModNode(ctx.getText(), "Mod"))
        else:
            self.substituteTraceBottom(BinaryopNode(ctx.getText(), "Bi"))
        self.skip()
        self.trace[-1].parent = self.trace[-2]

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



    def isTerminalType(self, node: ParserRuleContext, terminalID: int):
        return isinstance(node, TerminalNodeImpl) and node.symbol.type == terminalID

    def substituteTraceBottom(self, substitute: ASTree):
        bottom: ASTree = self.trace[-1]
        substitute.children.extend(bottom.children)
        bottom.children.clear()

        bottomParent = self.trace[-2]
        bottomParent.children[bottomParent.children.index(bottom)] = substitute

        self.trace[-1] = substitute
        self.current = substitute
