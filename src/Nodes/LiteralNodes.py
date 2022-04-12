from src.Nodes.ASTreeNode import LiteralNode
from src.SymbolTable import TypeList, VariableCType, CType
from src.Visitor import ASTreeVisitor
from src.Nodes.BuiltinInfo import BuiltinRanks, BuiltinNames


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

    def inferType(self, typeList: TypeList) -> CType:
        return VariableCType(typeList[BuiltinNames.INT])

    def getValue(self):
        return int(self.value)

    def rank(self) -> int:
        return BuiltinRanks.INT

    def __repr__(self):
        return str(self.getValue())


class FloatNode(LiteralNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def inferType(self, typeList: TypeList) -> CType:
        return VariableCType(typeList[BuiltinNames.FLOAT])

    def getValue(self):
        return float(self.value)

    def rank(self) -> int:
        return BuiltinRanks.FLOAT

    def __repr__(self):
        return str(self.getValue())


class CharNode(LiteralNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def inferType(self, typeList: TypeList) -> CType:
        return VariableCType(typeList[BuiltinNames.CHAR])

    def getValue(self):
        return str(self.value)

    def rank(self) -> int:
        return BuiltinRanks.CHAR

    def __repr__(self):
        return self.getValue()


def coerce(operand: LiteralNode, rank: int):
    if rank == BuiltinRanks.CHAR:
        return CharNode(operand.value, "Ch")
    elif rank == BuiltinRanks.INT:
        return IntegerNode(operand.value, "In")
    elif rank == BuiltinRanks.FLOAT:
        return FloatNode(operand.value, "Fl")
    else:
        return None
