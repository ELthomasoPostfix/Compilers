from src.Nodes.LiteralNodes import promote, coerce
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
            for child in value.children:
                if isinstance(child, BinaryopNode):
                    child.parent = value
                    self.visitBinaryop(child)
            if isinstance(value.children[0], LiteralNode) and isinstance(value.children[1], LiteralNode):
                child1, child2 = promote(value.children[0], value.children[1])
                val = value.evaluate(child1, child2)
                value.children = []

                value.replaceSelf(coerce(LiteralNode(val, "Li", value.parent), child1.rank()))

                # cleanup
                value.parent = []
                del value
        # TODO: Bestaat value nog?

    def visitUnaryexpression(self, value: UnaryexpressionNode):
        if len(value.children) == 2:
            if isinstance(value.children[0], NegativeNode) or isinstance(value.children[0], PositiveNode):
                #################################################################################
                # Value.children[0] is replaced by an integer node. So promote() can be called. #
                # Ex. (- , UnaryOpNode) => (-1, IntegerNode)                                    #
                # TODO: Misschien efficientere manier?                                          #
                #################################################################################
                val = 1
                if value.children[0].value == '-':
                    val = -1
                value.children[0].replaceSelf(coerce(LiteralNode(val, "Li", value.parent), 4))

                child0, child1 = promote(value.children[0], value.children[1])
                temp = child1.getValue()

                val = int(child0.value) * temp
                value.children = []
                value.replaceSelf(coerce(LiteralNode(val, "Li", value.parent), child1.rank()))
                value.parent = []
                del value

    def visitUnaryOp(self, value: UnaryopNode):
        pass
