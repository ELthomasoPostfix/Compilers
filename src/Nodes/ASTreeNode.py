from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree


class CfileNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitCfile(self)


class BlockNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBlock(self)


class StatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)


class ExpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExpression(self)


class UnaryopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


class RelationalopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitRelationalop(self)


class LiteralNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)


class LvalNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLval(self)


class QualifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifier(self)
