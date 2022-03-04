from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree


class ExpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExpression(self)


class StatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)


class ValueNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitValue(self)


class UnaryOpNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryOp(self)


class RelationalOpNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitrelationalOp(self)
