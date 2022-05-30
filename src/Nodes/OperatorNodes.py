import copy

from src.Nodes.ASTreeNode import *
from src.Enumerations import LLVMKeywords as llk, MIPSKeywords as mk


class SumNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() + right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.SUM

    @staticmethod
    def getMIPSROpKeyword(instructionType: str) -> str:
        if instructionType == "I":
            return mk.I_ADD
        elif instructionType[0] == "R":
            return mk.R_ADD

    def __str__(self):
        return '+'


class MinNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() - right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.MIN

    @staticmethod
    def getMIPSROpKeyword(instructionType: str) -> str:
        if instructionType == "I":
            return mk.I_MIN
        elif instructionType[0] == "R":
            return mk.R_MIN

    def __str__(self):
        return '-'


class MulNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() * right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.MUL

    @staticmethod
    def getMIPSROpKeyword(instructionType: str) -> str:
        if instructionType[0] == "I":
            return mk.S_MUL_N
        if instructionType[0] == "R":
            if instructionType[1] == "N":
                return mk.S_MUL_N
            elif instructionType[1] == "O":
                return mk.S_MUL_O

    def __str__(self):
        return '*'


class DivNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() / right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.DIV

    @staticmethod
    def getMIPSROpKeyword(instructionType: str) -> str:
        if instructionType[0] == "I":
            return mk.S_DIV
        if instructionType[0] == "R":
            return mk.S_DIV

    def __str__(self):
        return '/'


class ModNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() % right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.MOD

    @staticmethod
    def getMIPSROpKeyword(instructionType: str) -> str:
        if instructionType[0] in ["R", "I"]:
            return mk.S_REM

    def __str__(self):
        return '%'


class EqNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() == right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return f"{llk.COMPARE} {llk.EQ}"

    def __str__(self):
        return '=='


class NeqNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() != right.getValue()

    def __str__(self):
        return '!='


class GtNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() > right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return f"{llk.COMPARE} {llk.GT}"

    def __str__(self):
        return '>'


class GteNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() >= right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return f"{llk.COMPARE} {llk.GTE}"

    def __str__(self):
        return '>='


class LtNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() < right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return f"{llk.COMPARE} {llk.LT}"

    def __str__(self):
        return '<'


class LteNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() <= right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return f"{llk.COMPARE} {llk.LTE}"

    def __str__(self):
        return '<='


class AndNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() and right.getValue()     # TODO coerce operand to bool type

    def getLLVMOpKeyword(self) -> str:
        return llk.AND

    def __str__(self):
        return '&&'


class OrNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() or right.getValue()     # TODO coerce operand to bool type

    def getLLVMOpKeyword(self) -> str:
        return llk.OR

    def __str__(self):
        return '||'


class PositiveNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        return + value.getValue()

    def __str__(self):
        return '+'


class NegativeNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        return - value.getValue()

    def __str__(self):
        return '-'


class NotNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        return not value.getValue()

    def __str__(self):
        return '!'


class AddressOfNode(UnaryopNode):
    def inferType(self, typeList: TypeList):
        resultType: CType = copy.deepcopy(super().inferType(typeList))
        return resultType.addPointer(False)

    def evaluate(self, value: LiteralNode):
        pass

    def __str__(self):
        return '&'


class DereferenceNode(UnaryopNode):
    def inferType(self, typeList: TypeList):
        resultType: CType = copy.deepcopy(super().inferType(typeList))
        return resultType.removePointer()

    def evaluate(self, value: LiteralNode):
        pass

    def __str__(self):
        return '*'


class PrefixIncrementNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        pass

    def __str__(self):
        return '++.'


class PostfixIncrementNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        pass

    def __str__(self):
        return '.++'


class PrefixDecrementNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        pass

    def __str__(self):
        return '--.'


class PostfixDecrementNode(UnaryopNode):
    def evaluate(self, value: LiteralNode):
        pass

    def __str__(self):
        return '.--'


class ArraySubscriptNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        pass

    def getLLVMOpKeyword(self) -> str:
        return super().getLLVMOpKeyword()

    def __str__(self):
        return "[ ]"
