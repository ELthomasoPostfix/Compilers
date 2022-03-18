from src.Nodes.ASTreeNode import LiteralNode
from src.Visitor import ASTreeVisitor
from src.Nodes.PrimitiveRanks import PrimitiveRanks


def promote(left: LiteralNode, right: LiteralNode) -> [LiteralNode, LiteralNode]:
    if left.rank() == right.rank():
        return left, right
    elif left.rank() < right.rank():
        return coerce(left, right.rank()), right
    else:
        return left, coerce(right, left.rank())


class IntegerNode(LiteralNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def getValue(self):
        return int(self.value)

    def rank(self) -> int:
        return PrimitiveRanks.INT

    def __repr__(self):
        return str(self.getValue())


class FloatNode(LiteralNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def getValue(self):
        return float(self.value)

    def rank(self) -> int:
        return PrimitiveRanks.FLOAT

    def __repr__(self):
        return str(self.getValue())


class CharNode(LiteralNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def getValue(self):
        return str(self.value)

    def rank(self) -> int:
        return PrimitiveRanks.CHAR

    def __repr__(self):
        return self.getValue()





def coerce(operand: LiteralNode, rank: int):
    if rank == 2:
        return CharNode(operand.value, "Ch")
    elif rank == 4:
        return IntegerNode(operand.value, "In")
    elif rank == 7:
        return FloatNode(operand.value, "Fl")
    else:
        return None
