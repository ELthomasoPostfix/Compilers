from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import SelectionstatementNode


class IfNode(SelectionstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)

    def __repr__(self):
        return "if"


class ElseNode(SelectionstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)

    def __repr__(self):
        return "else"
