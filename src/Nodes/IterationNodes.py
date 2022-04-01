from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import IterationstatementNode


class WhileNode(IterationstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)

    def __repr__(self):
        return "while"
