from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from src.Nodes.IterationNodes import WhileNode, DoWhileNode
from src.Nodes.LiteralNodes import *
from src.Nodes.OperatorNodes import *
from src.generated.MyGrammarListener import MyGrammarListener
from src.generated.MyGrammarParser import MyGrammarParser


class ASTreeListener(MyGrammarListener):
    def __init__(self):
        self.root: ASTree = None
        self.current: ASTree = self.root

        self.pushDepths = []
        self.cstDepth = 0


    def addCurrentChild(self, node):
        """
        Add node as a child to self.current,
        This function should only be called once per overwritten enterRule() method.
        :param node: The node to add as a child
        """
        if self.current is None:
            self.root = node
        else:
            self.current.addChild(node)

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

    def enterWhilestatement(self, ctx:MyGrammarParser.WhilestatementContext):
        self.addCurrentChild(WhileNode(ctx.getText(), "While"))

    def exitWhilestatement(self, ctx:MyGrammarParser.WhilestatementContext):
        if len(self.current.children) == 1:
            self.current.addChild(NullstatementNode(ctx.getText(), "no-op"))

    def enterDowhilestatement(self, ctx:MyGrammarParser.DowhilestatementContext):
        self.addCurrentChild(DoWhileNode(ctx.getText(), "Do While"))

    def exitDowhilestatement(self, ctx:MyGrammarParser.DowhilestatementContext):
        if len(self.current.children) == 1:
            self.current.addChild(NullstatementNode(ctx.getText(), "no-op"), 0)

    def exitForexpression(self, ctx:MyGrammarParser.ForexpressionContext):
        i = ctx.parentCtx.children.index(ctx)   # TODO   Add a WhileNode and attach the for loop condition, followed by the for loop body statements, followed by the for loop increment expression
        pass

    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        if isinstance(ctx.children[0], MyGrammarParser.LiteralContext) or \
                self.isTerminalType(ctx.children[0], MyGrammarParser.LPAREN):
            return
        else:
            self.addCurrentChild(ExpressionNode(ctx.getText(), "Ex"))

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

    def enterUnaryexpression(self, ctx: MyGrammarParser.UnaryexpressionContext):
        self.addCurrentChild(UnaryexpressionNode(ctx.getText(), "Un"))

    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        self.addCurrentChild(UnaryopNode(ctx.getText(), "Un"))

    def enterVar_decl(self, ctx: MyGrammarParser.Var_declContext):
        self.addCurrentChild(Var_declNode(ctx.getText(), "Vd"))

    def enterVar_assig(self, ctx: MyGrammarParser.Var_assigContext):
        self.addCurrentChild(Var_assigNode(ctx.getText(), "Va"))

    def enterDeclarator(self, ctx: MyGrammarParser.DeclaratorContext):
        if not isinstance(self.current, DeclaratorNode):
            self.addCurrentChild(DeclaratorNode(ctx.getText(), "De"))

    def enterTypedeclaration(self, ctx:MyGrammarParser.TypedeclarationContext):
        self.addCurrentChild(TypedeclarationNode(ctx.getText(), "Td"))

    def enterLiteral(self, ctx: MyGrammarParser.LiteralContext):
        if self.isTerminalType(ctx.getChild(0), MyGrammarParser.INT):
            self.addCurrentChild(IntegerNode(ctx.getText(), "In"))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.FLOAT):
            self.addCurrentChild(FloatNode(ctx.getText(), "Fl"))

    def enterPointer(self, ctx: MyGrammarParser.PointerContext):
        self.addCurrentChild(PointerNode(ctx.getText(), "Pt"))

    def enterIdentifier(self, ctx: MyGrammarParser.IdentifierContext):
        self.addCurrentChild(IdentifierNode(ctx.getText(), "Id"))

    def enterTypespecifier(self, ctx: MyGrammarParser.TypequalifierContext):
        self.addCurrentChild(TypespecifierNode(ctx.getText(), "Ts"))

    def enterTypequalifier(self, ctx: MyGrammarParser.TypequalifierContext):
        if isinstance(self.current, TypedeclarationNode):
            firstChild = self.current.getChild(0)
            if firstChild is None or not isinstance(firstChild, TypequalifierNode):
                self.current.addChild(TypequalifierNode(ctx.getText(), "Tq"), 0)
        elif isinstance(self.current.getChild(-1), PointerNode):
            self.current.getChild(-1).addChild(TypequalifierNode(ctx.getText(), "Tq"))
        else:
            print("Invalid parent for TypequalifierNode")

    def isTerminalType(self, node: ParserRuleContext, terminalID: int):
        return isinstance(node, TerminalNodeImpl) and node.symbol.type == terminalID

