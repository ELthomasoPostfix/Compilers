from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree


class ExpNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExp(self)


class ValueExpNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitValueExp(self)


class ValueNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitValue(self)


class BopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBop(self)
