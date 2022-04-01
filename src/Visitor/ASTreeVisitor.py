class ASTree:
    def __init__(self):
        self.children = None


class CfileNode:
    pass
class BlockNode:
    pass
class StatementNode:
    pass
class ExpressionstatementNode:
    pass
class CompoundstatementNode:
    pass
class LabelstatementNode:
    pass
class SelectionstatementNode:
    pass
class IterationstatementNode:
    pass
class JumpstatementNode:
    pass
class NullstatementNode:
    pass
class ExpressionNode:
    pass
class UnaryexpressionNode:
    pass
class UnaryopNode:
    pass
class ForConditionNode:
    pass
class ForinitclauseNode:
    pass
class ForexpressionNode:
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

    def visitBinaryop(self, node: ASTree):
        pass



    def visitCfile(self, node: CfileNode):
        pass

    def visitBlock(self, node: BlockNode):
        pass

    def visitStatement(self, node: StatementNode):
        pass

    def visitExpressionstatement(self, node: ExpressionstatementNode):
        pass

    def visitCompoundstatement(self, node: CompoundstatementNode):
        pass

    def visitLabelstatement(self, node: LabelstatementNode):
        pass

    def visitSelectionstatement(self, node: SelectionstatementNode):
        pass

    def visitIterationstatement(self, node: IterationstatementNode):
        pass

    def visitJumpstatement(self, node: JumpstatementNode):
        pass

    def visitNullstatement(self, node: NullstatementNode):
        pass

    def visitExpression(self, node: ExpressionNode):
        pass

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        pass

    def visitUnaryop(self, node: UnaryopNode):
        pass

    def visitForCondition(self, node: ForConditionNode):
        pass

    def visitForinitclause(self, node: ForinitclauseNode):
        pass

    def visitForexpression(self, node: ForexpressionNode):
        pass

    def visitVar_decl(self, node: Var_declNode):
        pass

    def visitVar_assig(self, node: Var_assigNode):
        pass

    def visitDeclarator(self, node: DeclaratorNode):
        pass

    def visitTypedeclaration(self, node: TypedeclarationNode):
        pass

    def visitQualifiers(self, node: QualifiersNode):
        pass

    def visitQualifier(self, node: QualifierNode):
        pass

    def visitTypequalifier(self, node: TypequalifierNode):
        pass

    def visitTypespecifier(self, node: TypespecifierNode):
        pass

    def visitPointer(self, node: PointerNode):
        pass

    def visitLiteral(self, node: LiteralNode):
        pass

    def visitIdentifier(self, node: IdentifierNode):
        pass

