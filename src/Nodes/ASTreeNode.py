from src.ASTree.Element import ASTreeVisitor
from src.ASTree.ASTree import ASTree



class CfileNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitCfile(self)


class BlockNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBlock(self)


class StatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)


class IterationstatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIterationstatement(self)


class NullstatementNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitStatement(self)

    def __repr__(self):
        return self.name


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


class IdentifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitIdentifier(self)

    def __repr__(self):
        return self.value


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
