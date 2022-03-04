class ExpressionNode:
    pass
class StatementNode:
    pass
class ValueNode:
    pass
class UnaryOpNode:
    pass
class relationalOpNode:
    pass


class ASTreeVisitor:
    def visitExpression(self, exp: ExpressionNode):
        pass

    def visitStatement(self, value: StatementNode):
        pass

    def visitValue(self, value: ValueNode):
        pass

    def visitUnaryOp(self, value: UnaryOpNode):
        pass

    def visitRelationalOp(self, value: relationalOpNode):
        pass

