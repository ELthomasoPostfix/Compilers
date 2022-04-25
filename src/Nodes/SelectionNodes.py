from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import SelectionstatementNode


class IfNode(SelectionstatementNode):
    def __str__(self):
        return "if"


class ElseNode(SelectionstatementNode):
    def __str__(self):
        return "else"
