class ASTree:
    def __init__(self):
        self.children = None


class CfileNode:
    pass
class BlockNode:
    pass
class IncludedirectiveNode:
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
class SelectionelseNode:
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
class FunctioncallNode:
    pass
class UnaryopNode:
    pass
class ForConditionNode:
    pass
class ForinitclauseNode:
    pass
class ForexpressionNode:
    pass
class DeclarationNode:
    pass
class VariabledeclarationNode:
    pass
class Var_assigNode:
    pass
class AssignmentNode:
    pass
class FunctiondefinitionNode:
    pass
class FunctiondeclarationNode:
    pass
class ExpressionlistNode:
    pass
class DeclaratorNode:
    pass
class PointersandqualifiersNode:
    pass
class NoptrdeclaratorNode:
    pass
class FunctiondeclaratorNode:
    pass
class ParameterlistNode:
    pass
class FunctionparameterNode:
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
class RvalueNode:
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
        self.visitChildren(node)



    def visitCfile(self, node: CfileNode):
        self.visitChildren(node)

    def visitBlock(self, node: BlockNode):
        self.visitChildren(node)

    def visitIncludedirective(self, node: IncludedirectiveNode):
        self.visitChildren(node)

    def visitStatement(self, node: StatementNode):
        self.visitChildren(node)

    def visitExpressionstatement(self, node: ExpressionstatementNode):
        self.visitChildren(node)

    def visitCompoundstatement(self, node: CompoundstatementNode):
        self.visitChildren(node)

    def visitLabelstatement(self, node: LabelstatementNode):
        self.visitChildren(node)

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self.visitChildren(node)

    def visitSelectionelse(self, node: SelectionelseNode):
        self.visitChildren(node)

    def visitIterationstatement(self, node: IterationstatementNode):
        self.visitChildren(node)

    def visitJumpstatement(self, node: JumpstatementNode):
        self.visitChildren(node)

    def visitNullstatement(self, node: NullstatementNode):
        self.visitChildren(node)

    def visitExpression(self, node: ExpressionNode):
        self.visitChildren(node)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        self.visitChildren(node)

    def visitFunctioncall(self, node: FunctioncallNode):
        self.visitChildren(node)

    def visitUnaryop(self, node: UnaryopNode):
        self.visitChildren(node)

    def visitForCondition(self, node: ForConditionNode):
        self.visitChildren(node)

    def visitForinitclause(self, node: ForinitclauseNode):
        self.visitChildren(node)

    def visitForexpression(self, node: ForexpressionNode):
        self.visitChildren(node)

    def visitVariabledeclaration(self, node: VariabledeclarationNode):
        self.visitChildren(node)

    def visitVar_assig(self, node: Var_assigNode):
        self.visitChildren(node)

    def visitAssignment(self, node: AssignmentNode):
        self.visitChildren(node)

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        self.visitChildren(node)

    def visitFunctiondeclaration(self, node: FunctiondeclarationNode):
        self.visitChildren(node)

    def visitExpressionlist(self, node: ExpressionlistNode):
        self.visitChildren(node)

    def visitDeclarator(self, node: DeclaratorNode):
        self.visitChildren(node)

    def visitPointersandqualifiers(self, node: PointersandqualifiersNode):
        self.visitChildren(node)

    def visitNoptrdeclarator(self, node: NoptrdeclaratorNode):
        self.visitChildren(node)

    def visitFunctiondeclarator(self, node: FunctiondeclaratorNode):
        self.visitChildren(node)

    def visitParameterlist(self, node: ParameterlistNode):
        self.visitChildren(node)

    def visitFunctionparameter(self, node: FunctionparameterNode):
        self.visitChildren(node)

    def visitTypedeclaration(self, node: TypedeclarationNode):
        self.visitChildren(node)

    def visitQualifiers(self, node: QualifiersNode):
        self.visitChildren(node)

    def visitQualifier(self, node: QualifierNode):
        self.visitChildren(node)

    def visitTypequalifier(self, node: TypequalifierNode):
        self.visitChildren(node)

    def visitTypespecifier(self, node: TypespecifierNode):
        self.visitChildren(node)

    def visitPointer(self, node: PointerNode):
        self.visitChildren(node)

    def visitRvalue(self, node: RvalueNode):
        self.visitChildren(node)

    def visitLiteral(self, node: LiteralNode):
        self.visitChildren(node)

    def visitIdentifier(self, node: IdentifierNode):
        self.visitChildren(node)

