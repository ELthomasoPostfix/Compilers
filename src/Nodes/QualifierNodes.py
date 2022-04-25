from src.Nodes.ASTreeNode import QualifierNode


class ConstNode(QualifierNode):
    def __str__(self):
        return "const"
