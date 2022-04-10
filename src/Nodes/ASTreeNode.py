from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree
from src.SymbolTable import Record, SymbolTable
from abc import ABCMeta


class TypedNode(ASTree):
    __metaclass__ = ABCMeta

    """An abstract base class for nodes that are registered into the symbol table."""
    def __init__(self, value, name, parent=None):
        super().__init__(value, name, parent)
        self.record: Record = None

    def __repr__(self):
        return self.__str__() + "\\n" + str(self.record)

    def __str__(self):
        return self.value


class ScopedNode(ASTree):
    __metaclass__ = ABCMeta

    """
    An abstract base class for nodes that are require a reference to a symbol table,
    as they introduce a new scope.
    """

    def __init__(self, value, name, parent=None):
        super().__init__(value, name, parent)
        self.symbolTable: SymbolTable = None

    def __repr__(self):
        return self.__str__() + f"\\nhasST: {self.symbolTable is not None}"

    def __str__(self):
        return super().__str__()


class CfileNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitCfile(self)


class BlockNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBlock(self)


class CompoundstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitCompoundstatement(self)


class StatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)


class IterationstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)


class SelectionstatementNode(ScopedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitSelectionstatement(self)


class NullstatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)

    def __repr__(self):
        return self.name


# TODO  Give an expression a type member: char c = 1.1 / 4.1 MUST result in compile error due to lack of implicit conversions???
class ExpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExpression(self)


class UnaryexpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryexpression(self)


class UnaryopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)

    def __repr__(self):
        return self.value


class Var_declNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_decl(self)


class Var_assigNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_assig(self)


class DeclaratorNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitDeclarator(self)


class TypedeclarationNode(ASTree):
    def __init__(self, value, name, const: bool = False):
        super().__init__(value, name)
        self.const: bool = const

    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypedeclaration(self)


class QualifiersNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifiers(self)


class QualifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifier(self)

    def __repr__(self):
        return self.value


class TypequalifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypequalifier(self)

    def __repr__(self):
        return self.value


class TypespecifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitTypespecifier(self)

    def __repr__(self):
        return self.value


class LiteralNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def rank(self) -> int:
        pass

    def getValue(self):
        pass

    def __repr__(self):
        return self.getValue()


class IdentifierNode(TypedNode):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIdentifier(self)



# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode
class FunctionNode(TypedNode):
    pass
# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode
# TODO  make sure function inherits from TypedNode


class BinaryopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        pass


class PointerNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitPointer(self)

    def __repr__(self):
        return self.value
