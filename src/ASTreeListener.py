from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from src.Exceptions.exceptions import DeclarationException
from src.Nodes.IterationNodes import WhileNode, DoWhileNode
from src.Nodes.JumpNodes import ContinueNode, BreakNode, ReturnNode
from src.Nodes.SelectionNodes import IfNode, ElseNode
from src.Nodes.LiteralNodes import CharNode, IntegerNode, FloatNode
from src.Nodes.OperatorNodes import *
from src.Nodes.ASTreeNode import CompoundstatementNode
from src.generated.MyGrammarListener import MyGrammarListener
from src.generated.MyGrammarParser import MyGrammarParser


class ASTreeListener(MyGrammarListener):
    def __init__(self):
        self.root: ASTree = None
        self.current: ASTree = self.root

        self.pushDepths = []
        self.cstDepth = 0


    def addCurrentChild(self, node: ASTree):
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

    def replaceCurrent(self, replacement: ASTree):
        self.current.replaceSelf(replacement)
        self.current = replacement

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

    def enterCompoundstatement(self, ctx:MyGrammarParser.CompoundstatementContext):
        if len(ctx.children) == 2:
            self.addCurrentChild(self.createNoopNode(ctx.getText()))
        elif isinstance(self.current, BlockNode) or isinstance(self.current, FunctiondefinitionNode):
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
            initClause = self.current.getChild(0)
            self.current.children.remove(initClause)
            self.current.parent.addChild(initClause, len(self.current.parent.children) - 1)

        # Move iteration expression to the back of the while body
        iterationExpr = self.current.children[1]
        self.current.children.remove(iterationExpr)
        self.current.children.append(iterationExpr)

    def enterForstatement(self, ctx:MyGrammarParser.ForstatementContext):
        self.addCurrentChild(WhileNode(ctx.getText(), "While"))

    def enterJumpstatement(self, ctx:MyGrammarParser.JumpstatementContext):
        jumpKeyword = ctx.getChild(0)
        if self.isTerminalType(jumpKeyword, MyGrammarParser.CONTINUE):
            self.addCurrentChild(ContinueNode(ctx.getText(), "Continue"))
        elif self.isTerminalType(jumpKeyword, MyGrammarParser.BREAK):
            self.addCurrentChild(BreakNode(ctx.getText(), "Break"))
        elif self.isTerminalType(jumpKeyword, MyGrammarParser.RETURN):
            self.addCurrentChild(ReturnNode(ctx.getText(), "Return"))

    def enterNullstatement(self, ctx:MyGrammarParser.NullstatementContext):
        self.addCurrentChild(self.createNoopNode(ctx.getText()))

    def enterMultiplicationexp(self, ctx:MyGrammarParser.MultiplicationexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.STAR):
            self.addCurrentChild(MulNode(ctx.getText(), "MUL"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.DIV):
            self.addCurrentChild(DivNode(ctx.getText(), "DIV"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MOD):
            self.addCurrentChild(ModNode(ctx.getText(), "MOD"))

    def enterAddexp(self, ctx:MyGrammarParser.AddexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.PLUS):
            self.addCurrentChild(SumNode(ctx.getText(), "SUM"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MIN):
            self.addCurrentChild(MinNode(ctx.getText(), "MIN"))

    def enterRelationalexp(self, ctx:MyGrammarParser.RelationalexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.LT):
            self.addCurrentChild(LtNode(ctx.getText(), "LT"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.LTE):
            self.addCurrentChild(LteNode(ctx.getText(), "LTE"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GT):
            self.addCurrentChild(GtNode(ctx.getText(), "GT"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GTE):
            self.addCurrentChild(GteNode(ctx.getText(), "GTE"))

    def enterEqualityexp(self, ctx:MyGrammarParser.EqualityexpContext):
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.EQ):
            self.addCurrentChild(EqNode(ctx.getText(), "EQ"))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.NEQ):
            self.addCurrentChild(NeqNode(ctx.getText(), "NEQ"))

    def enterAndexp(self, ctx:MyGrammarParser.AndexpContext):
        self.addCurrentChild(AndNode(ctx.getText(), "AND"))

    def enterOrexp(self, ctx:MyGrammarParser.AndexpContext):
        self.addCurrentChild(OrNode(ctx.getText(), "OR"))

    def possiblyAddUnaryExpressionNode(self):
        if not isinstance(self.current, UnaryexpressionNode):
            self.addCurrentChild(UnaryexpressionNode(None, "Un"))

    def removeUnneededUnaryExpressionNode(self):
        if len(self.current.children) == 1:
            self.replaceCurrent(self.current.getChild(0))

    def enterUnarypostfixexp(self, ctx:MyGrammarParser.UnarypostfixexpContext):
        self.possiblyAddUnaryExpressionNode()

    def exitUnarypostfixexp(self, ctx:MyGrammarParser.UnarypostfixexpContext):
        if self.isTerminalType(ctx.getChild(0), MyGrammarParser.INCR):
            self.current.addChild(PrefixIncrementNode(ctx.getText(), "Pre-Incr"))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.DECR):
            self.current.addChild(PrefixDecrementNode(ctx.getText(), "Pre-Decr"))
        self.removeUnneededUnaryExpressionNode()

    def enterUnaryprefixexp(self, ctx:MyGrammarParser.UnaryprefixexpContext):
        self.possiblyAddUnaryExpressionNode()
        if self.isTerminalType(ctx.getChild(-1), MyGrammarParser.INCR):
            self.current.addChild(PostfixIncrementNode(ctx.getText(), "Post-Incr"))
        elif self.isTerminalType(ctx.getChild(-1), MyGrammarParser.DECR):
            self.current.addChild(PostfixDecrementNode(ctx.getText(), "Post-Decr"))

    def exitUnaryprefixexp(self, ctx:MyGrammarParser.UnaryprefixexpContext):
        self.removeUnneededUnaryExpressionNode()

    def enterUnaryexp(self, ctx:MyGrammarParser.UnaryexpContext):
        self.possiblyAddUnaryExpressionNode()

    def exitUnaryexp(self, ctx: MyGrammarParser.UnaryexpContext):
        self.removeUnneededUnaryExpressionNode()


    def exitUnaryexpression(self, ctx:MyGrammarParser.UnaryexpressionContext):
        if self.isTerminalType(ctx.getChild(-1), MyGrammarParser.INCR):
            self.current.addChild(PostfixIncrementNode(ctx.getText(), "Post-Incr"))
        elif self.isTerminalType(ctx.getChild(-1), MyGrammarParser.DECR):
            self.current.addChild(PostfixDecrementNode(ctx.getText(), "Post-Decr"))

        if len(self.current.children) == 1:
            self.replaceCurrent(self.current.getChild(0))

    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        unaryop = ctx.getChild(0)
        if self.isTerminalType(unaryop, MyGrammarParser.PLUS):
            self.addCurrentChild(PositiveNode(ctx.getText(), "Pos"))
        elif self.isTerminalType(unaryop, MyGrammarParser.MIN):
            self.addCurrentChild(NegativeNode(ctx.getText(), "Neg"))
        elif self.isTerminalType(unaryop, MyGrammarParser.NOT):
            self.addCurrentChild(NotNode(ctx.getText(), "Not"))
        elif self.isTerminalType(unaryop, MyGrammarParser.REF) and not\
                self.siblingsChildIsTerminalType(ctx, 1, MyGrammarParser.STAR):
            self.addCurrentChild(AddressOfNode(ctx.getText(), "Addr"))
        elif self.isTerminalType(unaryop, MyGrammarParser.STAR) and not\
                self.siblingsChildIsTerminalType(ctx, -1, MyGrammarParser.REF):
            self.addCurrentChild(DereferenceNode(ctx.getText(), "Deref"))

    def enterVar_decl(self, ctx: MyGrammarParser.Var_declContext):
        self.addCurrentChild(Var_declNode(ctx.getText(), "Vd"))

    def exitVar_decl(self, ctx:MyGrammarParser.Var_declContext):
        if isinstance(self.current.getChild(1), FunctionDeclaratorNode):
            self.replaceCurrent(FunctiondeclarationNode(ctx.getText(), "Func declaration"))
            if len(self.current.children) == 3:
                raise DeclarationException(f"Function declared like variable: {ctx.getChild(0).getText()} {ctx.getChild(1).getText()} = {ctx.getChild(2).getText()[1:]}")

        # Split off assignment as a separate statement
        elif len(self.current.children) == 3:
            assig = Var_assigNode("", "declaration assig")
            assig.addChild(self.current.getIdentifierNode())
            assig.addChild(self.current.children[2].detachSelf())
            self.current.parent.addChild(assig)

    def enterVar_assig(self, ctx: MyGrammarParser.Var_assigContext):
        self.addCurrentChild(Var_assigNode(ctx.getText(), "Va"))

    def enterFunctiondefinition(self, ctx:MyGrammarParser.FunctiondefinitionContext):
        self.addCurrentChild(FunctiondefinitionNode(ctx.getText(), "func_def"))

    def enterDeclarator(self, ctx: MyGrammarParser.DeclaratorContext):
        if not isinstance(self.current, DeclaratorNode):
            self.addCurrentChild(DeclaratorNode(ctx.getText(), "Declarator"))

    def enterNoptrdeclarator(self, ctx:MyGrammarParser.NoptrdeclaratorContext):
        if not isinstance(self.current, DeclaratorNode):
            self.addCurrentChild(DeclaratorNode(ctx.getText(), "Declarator"))
        if self.isTerminalType(ctx.parentCtx.getChild(-1), MyGrammarParser.RBRACKET):
            self.replaceCurrent(ArrayDeclaratorNode(ctx.getText(), "Array Declarator"))
        elif self.isTerminalType(ctx.parentCtx.getChild(-1), MyGrammarParser.RPAREN):
            self.replaceCurrent(FunctionDeclaratorNode(ctx.getText(), "Func Declarator"))

    def enterFunctionparameter(self, ctx:MyGrammarParser.FunctionparameterContext):
        self.addCurrentChild(Var_declNode(ctx.getText(), "Func param"))

    def enterTypedeclaration(self, ctx:MyGrammarParser.TypedeclarationContext):
        self.addCurrentChild(TypedeclarationNode(ctx.getText(), "Td"))

    def enterLvaluefunctioncall(self, ctx:MyGrammarParser.LvaluefunctioncallContext):
        self.addCurrentChild(FunctioncallNode(ctx.getText(), "Func call"))

    def enterLvalueliteralstring(self, ctx:MyGrammarParser.LvalueliteralstringContext):
        self.addCurrentChild(CharNode(ctx.getText(), "String"))

    def enterLvaluearraysubscript(self, ctx:MyGrammarParser.LvaluearraysubscriptContext):
        #   & lvalue-expression [ expression ]
        # special case: & and the * that is implied in [] cancel each other,
        # only the addition implied in [] is evaluated
        if isinstance(self.current, AddressOfNode):
            self.current.replaceSelf(None)
            # TODO do implied addition
            return
        self.addCurrentChild(ArraySubscriptNode(ctx.getText(), "AS"))

    def enterLiteral(self, ctx: MyGrammarParser.LiteralContext):
        if self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_INT):
            self.addCurrentChild(IntegerNode(ctx.getText(), "Int"))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_FLOAT):
            self.addCurrentChild(FloatNode(ctx.getText(), "Float"))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_CHAR):
            self.addCurrentChild(CharNode(ctx.getText().strip("'"), "Char"))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_STRING):
            self.addCurrentChild(CharNode(ctx.getText()[:-1][1:], "String"))

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
        elif isinstance(self.current, DeclaratorNode) and\
                isinstance(self.current.getChild(-1), PointerNode):
            self.current.getChild(-1).makeConst(TypequalifierNode(ctx.getText(), "Tq"))
        else:
            print("Invalid parent for TypequalifierNode")

    def isTerminalType(self, node: ParserRuleContext, terminalID: int):
        return isinstance(node, TerminalNodeImpl) and node.symbol.type == terminalID

    def siblingsChildIsTerminalType(self, node: ParserRuleContext, sibling: int, terminalID: int):
        """Check whether the child at index zero of the sibling of node is a terminal node of the specified terminal
        id. """
        if sibling != -1 and sibling != 1:
            raise ValueError(f"Incorrect value for sibling parameter: got {sibling}, but expected -1 or 1")
        if node.parentCtx is None:
            return False

        index = node.parentCtx.children.index(node)

        return index >= 0 and\
               ((sibling == -1 and index > 0) or
                (sibling ==  1 and index < len(node.parentCtx.children)-1)) and\
               self.isTerminalType(node.parentCtx.children[index + sibling].getChild(0), terminalID)
