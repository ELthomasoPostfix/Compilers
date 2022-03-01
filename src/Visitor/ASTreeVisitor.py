class ExpNode:
    pass
class ValueExpNode:
    pass
class ValueNode:
    pass
class BopNode:
    pass


class ASTreeVisitor:
    def visitExp(self, exp: ExpNode):
        pass

    def visitValueExp(self, value: ValueExpNode):
        pass

    def visitValue(self, value: ValueNode):
        pass

    def visitBop(self, value: BopNode):
        pass

