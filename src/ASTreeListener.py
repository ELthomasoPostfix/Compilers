from __future__ import annotations

from typing import List

from antlr4 import ParserRuleContext
from antlr4.tree.Tree import TerminalNodeImpl

from src.CompilersUtils import coloredDef
from src.Exceptions.exceptions import DeclarationException, InitializationException
from src.Nodes.IterationNodes import WhileNode, DoWhileNode
from src.Nodes.JumpNodes import ContinueNode, BreakNode, ReturnNode
from src.Nodes.QualifierNodes import ConstNode
from src.Nodes.SelectionNodes import IfNode, ElseNode
from src.Nodes.LiteralNodes import CharNode, IntegerNode, FloatNode
from src.Nodes.OperatorNodes import *
from src.Nodes.ASTreeNode import CompoundstatementNode
from src.generated.MyGrammarListener import MyGrammarListener
from src.generated.MyGrammarParser import MyGrammarParser
from src.Nodes.ASTreeNode import IncludedirectiveNode


class ASTreeListener(MyGrammarListener):
    def __init__(self, typeList: TypeList):
        self.root: ASTree | None = None
        self.current: ASTree | None = self.root
        self.typeList: TypeList = typeList

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

    def splitVariableInitialization(self, varDeclaration):
        assig = Var_assigNode(location=varDeclaration.location)
        assig.addChild(varDeclaration.getIdentifierNode())
        assig.addChild(varDeclaration.children[2].detachSelf())
        varDeclaration.parent.addChild(assig, varDeclaration.parent.children.index(varDeclaration) + 1)

    def returnLocation(self, ctx):
        return [ctx.start.line, ctx.start.column, ctx.stop.line, ctx.stop.column]

    def hasContextAncestor(self, ctx, ancestorCtx):
        """
        Check whether :ctx: has an ancestor of the specified
        type, using isinstance.

        :param ctx: The ctx to find an ancestor for
        :param ancestorCtx: The class to check for
        :return: Result
        """

        if ctx.parentCtx is None:
            return False
        elif isinstance(ctx.parentCtx, ancestorCtx):
            return True
        self.hasContextAncestor(ctx.parentCtx, ancestorCtx)

    def getStringContents(self, ctx):
        """
        Remove the first and last characters of the text of the ctx.
        
        :param ctx: The ctx to return the shortened text representation of
        :return: ctx.getText() minus its first and last characters
        """
        return ctx.getText()[:-1][1:]

    def enterEveryRule(self, ctx: ParserRuleContext):
        self.cstDepth += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        if self.cstDepth == self.pushDepths[-1]:
            self.pushDepths.pop(-1)
            self.current = self.current.parent
        self.cstDepth -= 1

    def enterCfile(self, ctx: MyGrammarParser.CfileContext):
        self.addCurrentChild(CfileNode(location=self.returnLocation(ctx)))

    def enterIncludedirective(self, ctx: MyGrammarParser.IncludedirectiveContext):
        # printf declaration
        self.addCurrentChild(IncludedirectiveNode(location=self.returnLocation(ctx)))

        # self.current.addChild(FunctiondeclarationNode()).\
        #     addChild(TypedeclarationNode()).\
        #     addChild(TypespecifierNode(BuiltinNames.INT))
        #
        # printfDeclaration = self.current.getChild(0)
        #
        # printfDeclaration.addChild(FunctionDeclaratorNode()).\
        #     addChild(IdentifierNode("printf"))

        # IncludeDirectiveNode = 4
        # param = VariabledeclarationNode()
        # param.addChild(TypedeclarationNode()).\
        #     addChild(TypespecifierNode(BuiltinNames.CHAR))      # Type specifier
        # param.getChild(0).addChild(ConstNode(), 0)    # const
        # param.addChild(DeclaratorNode()).\
        #     addChild(PointerNode())                             # pointer
        # param.getChild(1).addChild(IdentifierNode("format"))    # identifier (format)
        #
        # printfDeclaration.addChild(param)

        # scanf declaration
        # self.current.addChild(FunctiondeclarationNode()).\
        #     addChild(TypedeclarationNode()).\
        #     addChild(TypespecifierNode(BuiltinNames.VOID))
        #
        # scanfDeclaration = self.current.getChild(1)
        #
        # scanfDeclaration.addChild(FunctionDeclaratorNode()).\
        #     addChild(IdentifierNode("scanf"))
        # # TODO scanf parameters
        # print(coloredDef("The AST scanf declaration does not define any parameters"))

    def enterBlock(self, ctx: MyGrammarParser.BlockContext):
        self.addCurrentChild(BlockNode(location=[]))

    def enterCompoundstatement(self, ctx: MyGrammarParser.CompoundstatementContext):
        if isinstance(self.current, WhileNode) and len(ctx.children) == 2:
            self.addCurrentChild(NullstatementNode(location=self.returnLocation(ctx)))
        elif isinstance(self.current, BlockNode) or \
                isinstance(ctx.parentCtx.parentCtx, MyGrammarParser.CompoundstatementContext) or \
                isinstance(self.current, FunctiondefinitionNode):
            self.addCurrentChild(CompoundstatementNode(location=self.returnLocation(ctx)))

    def enterIfstatement(self, ctx: MyGrammarParser.IfstatementContext):
        self.addCurrentChild(IfNode())

    def exitIfstatement(self, ctx: MyGrammarParser.IfstatementContext):
        if not isinstance(self.current.children[-1], ElseNode):
            self.current.addChild(NullstatementNode())

    def enterSelectionelse(self, ctx: MyGrammarParser.SelectionelseContext):
        self.addCurrentChild(ElseNode())

    def enterWhilestatement(self, ctx: MyGrammarParser.WhilestatementContext):
        self.addCurrentChild(WhileNode())

    def exitWhilestatement(self, ctx: MyGrammarParser.WhilestatementContext):
        if len(self.current.children) == 1:
            self.current.addChild(NullstatementNode())

    def enterDowhilestatement(self, ctx: MyGrammarParser.DowhilestatementContext):
        self.addCurrentChild(DoWhileNode())

    def exitDowhilestatement(self, ctx: MyGrammarParser.DowhilestatementContext):
        if len(self.current.children) == 1:
            self.current.addChild(NullstatementNode(), 0)

    def exitForstatement(self, ctx: MyGrammarParser.ForstatementContext):
        if not isinstance(self.current, WhileNode):
            return

        forClause = ctx.children[2]
        initClauseMissing = self.isTerminalType(forClause.getChild(0), MyGrammarParser.SEMICOLON)
        iterConditionMissing = False
        iterExpressionMissing = False
        insertIndexes = []
        # This for loop does not include a branch/conditional for the init clause
        # of the for loop, because we will transform it into a while loop and push
        # the init clause up anyway, so inserting a noop is meaningless
        for idx, child in enumerate(forClause.children):
            if not self.isTerminalType(child, MyGrammarParser.SEMICOLON):
                continue
            if idx > 0 and self.isTerminalType(forClause.getChild(idx - 1), MyGrammarParser.SEMICOLON):
                iterConditionMissing = True
            if idx == len(forClause.children) - 1:
                iterExpressionMissing = True

        # Push up init clause
        if not initClauseMissing:
            initClause = self.current.getChild(0)
            self.current.children.remove(initClause)
            self.current.parent.addChild(initClause, len(self.current.parent.children) - 1)

            if len(initClause.children) == 3:
                self.splitVariableInitialization(initClause)

        # Missing iteration condition results in while(true)
        if iterConditionMissing:
            self.current.addChild(IntegerNode(1), 0)

        # Move iteration expression to the back of the while body
        if not iterExpressionMissing:
            # Remove noop from body being empty; iter expr. is still part of body
            if isinstance(self.current.getChild(-1), NullstatementNode):
                self.current.children.remove(self.current.getChild(-1))
            iterationExpression = self.current.children[1]  # iteration condition ensured to exist
            self.current.children.remove(iterationExpression)
            self.current.children.append(iterationExpression)

    def enterForstatement(self, ctx: MyGrammarParser.ForstatementContext):
        self.addCurrentChild(WhileNode())

    def enterJumpstatement(self, ctx: MyGrammarParser.JumpstatementContext):
        jumpKeyword = ctx.getChild(0)
        if self.isTerminalType(jumpKeyword, MyGrammarParser.CONTINUE):
            self.addCurrentChild(ContinueNode(location=self.returnLocation(ctx)))
        elif self.isTerminalType(jumpKeyword, MyGrammarParser.BREAK):
            self.addCurrentChild(BreakNode(location=self.returnLocation(ctx)))
        elif self.isTerminalType(jumpKeyword, MyGrammarParser.RETURN):
            self.addCurrentChild(ReturnNode(location=self.returnLocation(ctx)))

    def enterNullstatement(self, ctx: MyGrammarParser.NullstatementContext):
        self.addCurrentChild(NullstatementNode())

    def enterMultiplicationexp(self, ctx: MyGrammarParser.MultiplicationexpContext):
        location = self.returnLocation(ctx)
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.STAR):
            self.addCurrentChild(MulNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.DIV):
            self.addCurrentChild(DivNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MOD):
            self.addCurrentChild(ModNode(location=location))

    def enterAddexp(self, ctx: MyGrammarParser.AddexpContext):
        location = self.returnLocation(ctx)
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.PLUS):
            self.addCurrentChild(SumNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.MIN):
            self.addCurrentChild(MinNode(location=location))

    def enterRelationalexp(self, ctx: MyGrammarParser.RelationalexpContext):
        location = self.returnLocation(ctx)
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.LT):
            self.addCurrentChild(LtNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.LTE):
            self.addCurrentChild(LteNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GT):
            self.addCurrentChild(GtNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.GTE):
            self.addCurrentChild(GteNode(location=location))

    def enterEqualityexp(self, ctx: MyGrammarParser.EqualityexpContext):
        location = self.returnLocation(ctx)
        if self.isTerminalType(ctx.getChild(1), MyGrammarParser.EQ):
            self.addCurrentChild(EqNode(location=location))
        elif self.isTerminalType(ctx.getChild(1), MyGrammarParser.NEQ):
            self.addCurrentChild(NeqNode(location=location))

    def enterAndexp(self, ctx: MyGrammarParser.AndexpContext):
        self.addCurrentChild(AndNode(location=self.returnLocation(ctx)))

    def enterOrexp(self, ctx: MyGrammarParser.AndexpContext):
        self.addCurrentChild(OrNode(location=self.returnLocation(ctx)))

    def possiblyAddUnaryExpressionNode(self, ctx):
        if not isinstance(self.current, UnaryexpressionNode):
            self.addCurrentChild(UnaryexpressionNode(location=self.returnLocation(ctx)))

    def removeUnneededUnaryExpressionNode(self):
        if len(self.current.children) == 1:
            self.replaceCurrent(self.current.getChild(0))

    def enterUnarypostfixexp(self, ctx: MyGrammarParser.UnarypostfixexpContext):
        self.possiblyAddUnaryExpressionNode(ctx)

    def exitUnarypostfixexp(self, ctx: MyGrammarParser.UnarypostfixexpContext):
        if self.isTerminalType(ctx.getChild(-1), MyGrammarParser.INCR):
            self.current.addChild(PrefixIncrementNode(location=self.returnLocation(ctx)))
        elif self.isTerminalType(ctx.getChild(-1), MyGrammarParser.DECR):
            self.current.addChild(PrefixDecrementNode(location=self.returnLocation(ctx)))
        self.removeUnneededUnaryExpressionNode()

    def enterUnaryprefixexp(self, ctx: MyGrammarParser.UnaryprefixexpContext):
        self.possiblyAddUnaryExpressionNode(ctx)
        if self.isTerminalType(ctx.getChild(0), MyGrammarParser.INCR):
            self.current.addChild(PostfixIncrementNode(location=self.returnLocation(ctx)))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.DECR):
            self.current.addChild(PostfixDecrementNode(location=self.returnLocation(ctx)))

    def exitUnaryprefixexp(self, ctx: MyGrammarParser.UnaryprefixexpContext):
        self.removeUnneededUnaryExpressionNode()

    def enterUnaryexp(self, ctx: MyGrammarParser.UnaryexpContext):
        self.possiblyAddUnaryExpressionNode(ctx)

    def exitUnaryexp(self, ctx: MyGrammarParser.UnaryexpContext):
        self.removeUnneededUnaryExpressionNode()

    def enterUnaryop(self, ctx: MyGrammarParser.UnaryopContext):
        unaryop = ctx.getChild(0)
        location = self.returnLocation(ctx)
        if self.isTerminalType(unaryop, MyGrammarParser.PLUS):
            self.addCurrentChild(PositiveNode(location=location))
        elif self.isTerminalType(unaryop, MyGrammarParser.MIN):
            self.addCurrentChild(NegativeNode(location=location))
        elif self.isTerminalType(unaryop, MyGrammarParser.NOT):
            self.addCurrentChild(NotNode(location=location))
        elif self.isTerminalType(unaryop, MyGrammarParser.REF) and not \
                self.siblingsChildIsTerminalType(ctx, 1, MyGrammarParser.STAR):
            self.addCurrentChild(AddressOfNode(location=location))
        elif self.isTerminalType(unaryop, MyGrammarParser.STAR) and not \
                self.siblingsChildIsTerminalType(ctx, -1, MyGrammarParser.REF):
            self.addCurrentChild(DereferenceNode(location=location))

    def enterDeclaration(self, ctx: MyGrammarParser.DeclarationContext):
        self.addCurrentChild(VariabledeclarationNode(location=self.returnLocation(ctx)))

    def exitDeclaration(self, ctx: MyGrammarParser.DeclarationContext):
        if isinstance(self.current.getChild(1), FunctionDeclaratorNode):
            self.replaceCurrent(FunctiondeclarationNode(location = self.returnLocation(ctx)))
            if len(self.current.children) == 3:
                raise DeclarationException(
                    f"Function declared like variable: {ctx.getChild(0).getText()} {ctx.getChild(1).getText()} = {ctx.getChild(2).getText()[1:]}",location=self.returnLocation(ctx))

        # Split off assignment as a separate statement
        # Except for a for init clause, as the init var declaration must be pushed outside first
        if len(self.current.children) == 3 and not self.hasContextAncestor(ctx, MyGrammarParser.ForinitclauseContext):
            self.splitVariableInitialization(self.current)

    def enterVar_assig(self, ctx: MyGrammarParser.Var_assigContext):
        self.addCurrentChild(Var_assigNode(location=self.returnLocation(ctx)))

    def enterFunctiondefinition(self, ctx: MyGrammarParser.FunctiondefinitionContext):
        self.addCurrentChild(FunctiondefinitionNode(location=self.returnLocation(ctx)))

    def enterDeclarator(self, ctx: MyGrammarParser.DeclaratorContext):
        if not isinstance(self.current, DeclaratorNode):
            self.addCurrentChild(DeclaratorNode(location=self.returnLocation(ctx)))

    def enterNoptrdeclarator(self, ctx: MyGrammarParser.NoptrdeclaratorContext):
        if not isinstance(self.current, DeclaratorNode):
            self.addCurrentChild(DeclaratorNode(location=self.returnLocation(ctx)))
        if self.isTerminalType(ctx.parentCtx.getChild(-1), MyGrammarParser.RBRACKET):
            self.replaceCurrent(ArrayDeclaratorNode(location=self.returnLocation(ctx)))
        elif self.isTerminalType(ctx.parentCtx.getChild(-1), MyGrammarParser.RPAREN):
            self.replaceCurrent(FunctionDeclaratorNode(location=self.returnLocation(ctx)))

    def enterFunctionparameter(self, ctx: MyGrammarParser.FunctionparameterContext):
        self.addCurrentChild(VariabledeclarationNode(location = self.returnLocation(ctx)))

    def enterTypedeclaration(self, ctx: MyGrammarParser.TypedeclarationContext):
        self.addCurrentChild(TypedeclarationNode(location=self.returnLocation(ctx)))

    def enterLvaluefunctioncall(self, ctx: MyGrammarParser.LvaluefunctioncallContext):
        self.addCurrentChild(FunctioncallNode(location=self.returnLocation(ctx)))

    def enterLvalueliteralstring(self, ctx: MyGrammarParser.LvalueliteralstringContext):
        self.addCurrentChild(CharNode(self.getStringContents(ctx), location = self.returnLocation(ctx)))

    def enterLvaluearraysubscript(self, ctx: MyGrammarParser.LvaluearraysubscriptContext):
        #   & lvalue-expression [ expression ]
        # special case: & and the * that is implied in [] cancel each other,
        # only the addition implied in [] is evaluated
        if isinstance(self.current, AddressOfNode):
            self.current.replaceSelf(None)
            # TODO do implied addition
            return
        self.addCurrentChild(ArraySubscriptNode(location = self.returnLocation(ctx)))

    def enterLiteral(self, ctx: MyGrammarParser.LiteralContext):
        location = self.returnLocation(ctx)
        if self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_INT):
            self.addCurrentChild(IntegerNode(int(ctx.getText()), location=location))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_FLOAT):
            self.addCurrentChild(FloatNode(float(ctx.getText()), location=location))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_CHAR):
            char = self.getStringContents(ctx)
            if len(char) == 0:
                raise InitializationException("Empty char literal", location=location)
            self.addCurrentChild(CharNode(char, location=location))
        elif self.isTerminalType(ctx.getChild(0), MyGrammarParser.LITERAL_STRING):
            self.addCurrentChild(CharNode(self.getStringContents(ctx), location=location))

    def enterPointer(self, ctx: MyGrammarParser.PointerContext):
        self.addCurrentChild(PointerNode(location = self.returnLocation(ctx)))

    def enterIdentifier(self, ctx: MyGrammarParser.IdentifierContext):
        self.addCurrentChild(IdentifierNode(ctx.getText(),location=self.returnLocation(ctx)))

    def enterTypespecifier(self, ctx: MyGrammarParser.TypequalifierContext):
        self.addCurrentChild(TypespecifierNode(ctx.getText(), location=self.returnLocation(ctx)))

    def enterTypequalifier(self, ctx: MyGrammarParser.TypequalifierContext):
        location = self.returnLocation(ctx)
        if isinstance(self.current, TypedeclarationNode):
            firstChild = self.current.getChild(0)
            if firstChild is None or not isinstance(firstChild, QualifierNode):
                if self.isTerminalType(ctx.getChild(0), MyGrammarParser.QUALIFIER_CONST):
                    self.current.addChild(ConstNode(location=location), 0)
        elif isinstance(self.current, DeclaratorNode) and \
                isinstance(self.current.getChild(-1), PointerNode):
            self.current.getChild(-1).makeConst(ConstNode(location=location))
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

        return index >= 0 and \
               ((sibling == -1 and index > 0) or
                (sibling == 1 and index < len(node.parentCtx.children) - 1)) and \
               self.isTerminalType(node.parentCtx.children[index + sibling].getChild(0), terminalID)
