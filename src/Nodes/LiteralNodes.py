from __future__ import annotations

from src.CompilersUtils import ctoi
from src.Nodes.ASTreeNode import LiteralNode
from src.SymbolTable import TypeList, CType
from src.Enumerations import BuiltinRanks, BuiltinNames, LLVMKeywords


def promote(left: LiteralNode, right: LiteralNode) -> [LiteralNode, LiteralNode]:
    if left.rank() == right.rank():
        return left, right
    elif left.rank() < right.rank():
        return coerce(left, right.rank()), right
    else:
        return left, coerce(right, left.rank())


class IntegerNode(LiteralNode):
    @staticmethod
    def inferType(typeList: TypeList) -> CType:
        return CType(typeList[BuiltinNames.INT])

    @staticmethod
    def rank() -> int:
        return BuiltinRanks.INT

    def setValue(self, value) -> None:
        """
        Set the value of the LiteralNode.
        pre-cond: :value: is convertible to int type
        post-cond: value member of LiteralNode is assigned the passed value

        :param value: The new value of the LiteralNode
        """

        self._value = int(value)
        assert isinstance(self._value, int), f"{self.__class__.__name__} incorrectly set value: expected type {int}," \
                                             f" but got {type(self.getValue())}"

    def __repr__(self):
        return str(self.getValue())


class FloatNode(LiteralNode):
    @staticmethod
    def inferType(typeList: TypeList) -> CType:
        return CType(typeList[BuiltinNames.FLOAT])

    @staticmethod
    def rank() -> int:
        return BuiltinRanks.FLOAT

    def setValue(self, value) -> None:
        """
        Set the value of the LiteralNode.
        pre-cond: :value: is convertible to float type
        post-cond: value member of LiteralNode is assigned the passed value

        :param value: The new value of the LiteralNode
        """

        self._value = float(value)
        assert isinstance(self._value, float), f"{self.__class__.__name__} incorrectly set value: expected type {float},"\
                                               f" but got {type(self.getValue())}"

    def __repr__(self):
        return str(self.getValue())


# TODO  A string literal must be null terminated (\00 or \x00) and is converted to a char array.
#   Only array subscript can be applied to string literals.
class CharNode(LiteralNode):
    @staticmethod
    def inferType(typeList: TypeList) -> CType:
        return CType(typeList[BuiltinNames.CHAR])

    @staticmethod
    def rank() -> int:
        return BuiltinRanks.CHAR

    def setValue(self, value: str | int) -> None:
        """
        Set the value of the LiteralNode.
        pre-cond: :value: is a len 1 string convertible to an int, octal escape sequence, hex escape sequence or an int
        post-cond: value member of LiteralNode is assigned the passed value

        :param value: The new value of the LiteralNode
        """

        assert isinstance(value, int) or isinstance(value, str), f"Cannot construct {self.__class__.__name__} instance " \
                                                                 f"from {value.__class__.__name__} type value"

        self._value = ctoi(value) if isinstance(value, str) else value
        assert isinstance(self._value, int), f"{self.__class__.__name__} incorrectly set value: expected type {int}," \
                                             f" but got {type(self.getValue())}"

    def __repr__(self):
        return "'" + str(self.getValue()) + "'"


def coerce(operand: LiteralNode, rank: int):
    if rank == BuiltinRanks.CHAR:
        return CharNode(str(operand.getValue()))
    elif rank == BuiltinRanks.INT:
        return IntegerNode(int(operand.getValue()))
    elif rank == BuiltinRanks.FLOAT:
        return FloatNode(float(operand.getValue()))
    else:
        return None
