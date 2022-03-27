class ASTree:
    def __init__(self):
        self.children = None
class CfileNode:
    pass
class BlockNode:
    pass
class StatementNode:
    pass
class ExpressionNode:
    pass
class UnaryexpressionNode:
    pass
class UnaryopNode:
    pass
class Var_declNode:
    pass
class Var_assigNode:
    pass
class DeclaratorNode:
    pass
class TypedeclarationNode:
    pass
class QualifiersNode:
    pass
class QualifierNode:
    pass
class TypequalifierNode:
    pass
class TypespecifierNode:
    pass
class PointerNode:
    pass
class LiteralNode:
    pass
class IdentifierNode:
    pass



class ASTreeVisitor:
    def visitChildren(self, node: ASTree):
        for c in node.children:
            c.accept(self)

    def visitCfile(self, value: CfileNode):
        pass

    def visitBlock(self, value: BlockNode):
        pass

    def visitStatement(self, value: StatementNode):
        pass

    def visitExpression(self, value: ExpressionNode):
        pass

    def visitUnaryexpression(self, value: UnaryexpressionNode):
        pass

    def visitUnaryop(self, value: UnaryopNode):
        pass

    def visitVar_decl(self, value: Var_declNode):
        pass

    def visitVar_assig(self, value: Var_assigNode):
        pass

    def visitDeclarator(self, value: DeclaratorNode):
        pass

    def visitTypedeclaration(self, value: TypedeclarationNode):
        pass

    def visitQualifiers(self, value: QualifiersNode):
        pass

    def visitQualifier(self, value: QualifierNode):
        pass

    def visitTypequalifier(self, value: TypequalifierNode):
        pass

    def visitTypespecifier(self, value: TypespecifierNode):
        pass

    def visitPointer(self, value: PointerNode):
        pass

    def visitLiteral(self, value: LiteralNode):
        pass

    def visitIdentifier(self, value: IdentifierNode):
        pass

    def visitBinaryop(self, self1):
        pass

