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


class EqNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        mod = literals[0]
        del literals[0]
        for item in literals:
            mod = mod == item
        return mod

    def __repr__(self):
        return '=='


class NeqNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        mod = literals[0]
        del literals[0]
        for item in literals:
            mod = mod != item
        return mod

    def __repr__(self):
        return '!='


class GtNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        great = literals[0]
        del literals[0]
        for item in literals:
            great = great > item
        return great

    def __repr__(self):
        return '>'


class GteNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        greateq = literals[0]
        del literals[0]
        for item in literals:
            greateq = greateq >= item
        return greateq

    def __repr__(self):
        return '>='


class LtNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        less = literals[0]
        del literals[0]
        for item in literals:
            less = less < item
        return less

    def __repr__(self):
        return '<'


class LteNode(BinaryopNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluateLiterals(self, literals: list):
        lesseq = literals[0]
        del literals[0]
        for item in literals:
            lesseq = lesseq <= item
        return lesseq

    def __repr__(self):
        return '<='

