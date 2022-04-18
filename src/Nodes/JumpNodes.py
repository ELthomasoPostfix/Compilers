from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import JumpstatementNode
from src.Nodes.ASTreeNode import IterationstatementNode, FunctiondefinitionNode


class ContinueNode(JumpstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)

    def __str__(self):
        return "continue"


class BreakNode(JumpstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)

    def __str__(self):
        return "break"


class ReturnNode(JumpstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)

    def __str__(self):
        return "return"
