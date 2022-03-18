from src.Nodes.ASTreeNode import *


class SumNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
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

