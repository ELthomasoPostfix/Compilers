from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import IterationstatementNode


class WhileNode(IterationstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)

    def __str__(self):
        return "while"


class DoWhileNode(IterationstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)

    def __str__(self):
        return "do while"
