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


class ExpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitExpression(self)


class LiteralNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLiteral(self)

    def rank(self) -> int:
        pass

    def getValue(self):
        pass


class BinaryopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitBinaryop(self)

    def evaluate(self, left: LiteralNode, right: LiteralNode):
        pass


class UnaryexpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryexpression(self)


class ValueexpressionNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitValueexpression(self)


class UnaryopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitUnaryop(self)


class RelationalopNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitRelationalop(self)


class LvalNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitLval(self)


class C_typeNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitC_type(self)


class QualifierNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitQualifier(self)


class Var_declNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_decl(self)


class Var_assigNode(ASTree):
    def accept(self, visitor: ASTreeVisitor):
        visitor.visitVar_assig(self)





