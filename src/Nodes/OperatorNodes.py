from src.Nodes.ASTreeNode import *


class SumNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        a = left.getValue()
        b = right.getValue()
        c = a + b
        return left.getValue() + right.getValue()

    def __repr__(self):
        return '+'


class MinNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() - right.getValue()

    def __repr__(self):
        return '-'


class MulNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() * right.getValue()

    def __repr__(self):
        return '*'


class DivNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() / right.getValue()

    def __repr__(self):
        return '/'


class ModNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() % right.getValue()

    def __repr__(self):
        return '%'


class EqNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() == right.getValue()

    def __repr__(self):
        return '=='


class NeqNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() != right.getValue()

    def __repr__(self):
        return '!='


class GtNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() > right.getValue()

    def __repr__(self):
        return '>'


class GteNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() >= right.getValue()


    def __repr__(self):
        return '>='


class LtNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() < right.getValue()


    def __repr__(self):
        return '<'


class LteNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() <= right.getValue()


    def __repr__(self):
        return '<='


class AndNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() and right.getValue()     # TODO coerce operand to bool type


    def __repr__(self):
        return '&&'


class OrNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        return left.getValue() or right.getValue()     # TODO coerce operand to bool type


    def __repr__(self):
        return '||'


class PositiveNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '+'


class NegativeNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '-'


class NotNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '!'


class AddressOfNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '&'


class DereferenceNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '*'


class PrefixIncrementNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '++.'


class PostfixIncrementNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '.++'


class PrefixDecrementNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '--.'


class PostfixDecrementNode(UnaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


    def __repr__(self):
        return '.--'


class ArraySubscriptNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)


    def __repr__(self):
        return "[ ]"
