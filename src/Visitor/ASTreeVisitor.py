from src.ASTree import ASTree


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
class ValueexpressionNode:
    pass
class UnaryopNode:
    pass
class RelationalopNode:
    pass
class LiteralNode:
    pass
class LvalNode:
    pass
class C_typeNode:
    pass
class QualifierNode:
    pass
class Var_declNode:
    pass
class Var_assigNode:
    pass
class BinaryopNode:
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

    def visitBinaryop(self, value: BinaryopNode):
        pass

    def visitUnaryexpression(self, value: UnaryexpressionNode):
        pass

    def visitValueexpression(self, value: ValueexpressionNode):
        pass

    def visitUnaryop(self, value: UnaryopNode):
        pass

    def visitRelationalop(self, value: RelationalopNode):
        pass

    def visitLiteral(self, value: LiteralNode):
        pass

    def visitLval(self, value: LvalNode):
        pass

    def visitC_type(self, value: C_typeNode):
        pass

    def visitQualifier(self, value: QualifierNode):
        pass

    def visitVar_decl(self, value: Var_declNode):
        pass

    def visitVar_assig(self, value: Var_assigNode):
        pass

