from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import JumpstatementNode

class ContinueNode(JumpstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)

    def __repr__(self):
        return "continue"


class BreakNode(JumpstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)

    def __repr__(self):
        return "break"


class ReturnNode(JumpstatementNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitJumpstatement(self)

    def __repr__(self):
        return "return"
