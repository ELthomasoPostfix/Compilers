import copy

from src.Nodes.ASTreeNode import *
from src.Enumerations import LLVMKeywords as llk


class SumNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() + right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.SUM

    def __str__(self):
        return '+'


class MinNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() - right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.MIN

    def __str__(self):
        return '-'


class MulNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() * right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.MUL

    def __str__(self):
        return '*'


class DivNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() / right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.DIV

    def __str__(self):
        return '/'


class ModNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() % right.getValue()

    def getLLVMOpKeyword(self) -> str:
        return llk.MOD

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
