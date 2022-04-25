from src.Enumerations import BuiltinRanks
from src.Nodes.LiteralNodes import promote, coerce, IntegerNode, CharNode
from src.Nodes.OperatorNodes import NegativeNode, PositiveNode
from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import *
from src.CompilersUtils import coloredDef


class OptimizationVisitor(ASTreeVisitor):
    def visitCfile(self, value: CfileNode):
        self.visitChildren(value)

    def visitBlock(self, value: BlockNode):
        self.visitChildren(value)

    def visitStatement(self, value: StatementNode):
        self.visitChildren(value)

    def visitExpression(self, exp: ExpressionNode):
        self.visitChildren(exp)

    def visitLiteral(self, value: LiteralNode):
        pass

    def visitBinaryop(self, value: BinaryopNode):
        self.visitChildren(value)
        if len(value.children) == 2:
            lhs: ASTree = value.getChild(0)
            rhs: ASTree = value.getChild(1)
            if isinstance(lhs, LiteralNode) and isinstance(rhs, LiteralNode):
                child1, child2 = promote(value.children[0], value.children[1])
                child1.setValue(value.evaluate(child1, child2))

                # detachment
                lhs.replaceSelf(None)
                rhs.replaceSelf(None)
                child1.replaceSelf(None)
                child2.replaceSelf(None)
                value.replaceSelf(child1)

    def visitUnaryexpression(self, value: UnaryexpressionNode):
        self.visitChildren(value)

        if len(value.children) >= 2 and isinstance(value.children[len(value.children) - 1], LiteralNode):
            literalIdx = len(value.children) - 1
            while literalIdx >= 0 and (isinstance(value.getChild(0), NegativeNode) or
                                       isinstance(value.getChild(0), PositiveNode)):
                #################################################################################
                # Value.children[0] is replaced by an integer node. So promote() can be called. #
                # Ex. (- , UnaryOpNode) => (-1, IntegerNode)                                    #
                # TODO: Misschien efficientere manier?                                          #
                #################################################################################
                val = 1
                if isinstance(value.getChild(literalIdx-1), NegativeNode):
                    val = -1

                uopFactor, literal = promote(IntegerNode(val, value), value.getChild(literalIdx))
                literal.setValue(literal.getValue() * uopFactor.getValue())

                value.getChild(literalIdx - 1).replaceSelf(None)
                literalIdx -= 1

            if len(value.children) == 1:
                value.replaceSelf(value.getChild(0))
                del value

    def visitUnaryOp(self, value: UnaryopNode):
        pass
