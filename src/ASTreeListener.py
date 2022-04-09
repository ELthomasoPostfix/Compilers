from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from src.Nodes.IterationNodes import WhileNode, DoWhileNode
from src.Nodes.SelectionNodes import IfNode, ElseNode
from src.Nodes.LiteralNodes import *
from src.Nodes.OperatorNodes import *
from src.Visitor.ASTreeVisitor import CompoundstatementNode
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

    def createNoopNode(self, value):
        return NullstatementNode(value, "no-op")

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

    def enterCompoundstatement(self, ctx: MyGrammarParser.CompoundstatementContext):
        if isinstance(self.current, BlockNode):
            self.addCurrentChild(CompoundstatementNode("", "Co"))

    def enterIfstatement(self, ctx:MyGrammarParser.IfstatementContext):
        self.addCurrentChild(IfNode(ctx.getText(), "If"))

    def exitIfstatement(self, ctx:MyGrammarParser.IfstatementContext):
        if not isinstance(self.current.children[-1], ElseNode):
            self.current.addChild(self.createNoopNode(ctx.getText()))

    def enterSelectionelse(self, ctx:MyGrammarParser.SelectionelseContext):
        self.addCurrentChild(ElseNode(ctx.getText(), "Else"))

    def enterWhilestatement(self, ctx:MyGrammarParser.WhilestatementContext):
        self.addCurrentChild(WhileNode(ctx.getText(), "While"))

    def exitWhilestatement(self, ctx:MyGrammarParser.WhilestatementContext):
        if len(self.current.children) == 1:
            self.current.addChild(self.createNoopNode(ctx.getText()))

    def enterDowhilestatement(self, ctx:MyGrammarParser.DowhilestatementContext):
        self.addCurrentChild(DoWhileNode(ctx.getText(), "Do While"))

    def exitDowhilestatement(self, ctx:MyGrammarParser.DowhilestatementContext):
        if len(self.current.children) == 1:
            self.current.addChild(self.createNoopNode(ctx.getText()), 0)

    def exitForstatement(self, ctx:MyGrammarParser.ForstatementContext):
        if not isinstance(self.current, WhileNode):
            return
        forClause = ctx.children[2]
        insertIndexes = []
        for idx, child in enumerate(forClause.children):
            if not isinstance(child, TerminalNodeImpl):
                continue
            if idx > 0 and isinstance(forClause.getChild(idx - 1), TerminalNodeImpl):
                insertIndexes.append(0)
            if idx == len(forClause.children) - 1:
                insertIndexes.append(1)

        for idx in insertIndexes:
            self.current.addChild(self.createNoopNode(None), idx)

        # Push up init clause
        if not self.isTerminalType(forClause.getChild(0), MyGrammarParser.SEMICOLON):
            declarationStatement = self.current.getChild(0)
            self.current.children.remove(declarationStatement)
            self.current.parent.addChild(declarationStatement, len(self.current.parent.children) - 1)

        # Move iteration expression to the back of the while body
        iterationExpr = self.current.children[1]
        self.current.children.remove(iterationExpr)
        self.current.children.append(iterationExpr)

    def enterForstatement(self, ctx:MyGrammarParser.ForstatementContext):
        self.addCurrentChild(WhileNode(ctx.getText(), "While"))

    def enterNullstatement(self, ctx:MyGrammarParser.NullstatementContext):
        self.addCurrentChild(self.createNoopNode(ctx.getText()))

    def enterCompoundstatement(self, ctx:MyGrammarParser.CompoundstatementContext):
        if len(ctx.children) == 2:
            self.addCurrentChild(self.createNoopNode(ctx.getText()))

    def enterExpression(self, ctx: MyGrammarParser.ExpressionContext):
        if not (isinstance(ctx.children[0], MyGrammarParser.LiteralContext) or
                self.isTerminalType(ctx.children[0], MyGrammarParser.LPAREN)):
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

