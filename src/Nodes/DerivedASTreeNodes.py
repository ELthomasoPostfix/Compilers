from src.Nodes.ASTreeNode import *


class SumNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        return sum(literals)

    def __repr__(self):
        return '+'


class MinNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        return min(literals)

    def __repr__(self):
        return '-'


class MulNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        mul = 1
        for item in literals:
            mul *= item
        return mul

    def __repr__(self):
        return '*'


class DivNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        div = literals[0]
        del literals[0]
        for item in literals:
            div /= item
        return div

    def __repr__(self):
        return '/'


class ModNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        mod = literals[0]
        del literals[0]
        for item in literals:
            mod %= item
        return mod

    def __repr__(self):
        return '%'

