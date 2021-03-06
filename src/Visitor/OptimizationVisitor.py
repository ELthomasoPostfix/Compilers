from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import *
from src.CompilersUtils import coloredDef
from fnmatch import *


class OptimizationVisitor:
    def visitStatement(self, value: StatementNode):
        print(coloredDef("STAT"), value.value, value.name)

    def visitExpression(self, exp: ExpressionNode):
        print(coloredDef("EXP"), exp.value, exp.name)

    def visitValue(self, value: ValueNode):
        print(coloredDef("VAL"), value.value, value.name)

    def visitBop(self, value: ValueNode):
        pass
        # if len(value.children) == 2:
        #     for child in value.children:
        #         if isinstance(child, BopNode):
        #             self.visitBop(child)
        #
        #     if value.children[0].name == 'VALUE' and value.children[1].name == 'VALUE':
        #         pass
        #
        #     val1 = value.children[0].value
        #     val2 = value.children[1].value
        #     value.children.clear()
        #
        #     value.name = 'VALUE'
        #
        #     # TODO: VERY UGLY !!! CHANGE
        #     if value.value == '+':
        #         value.value = int(val1) + int(val2)
        #     elif value.value == '-':
        #         value.value = int(val1) - int(val2)
        #     elif value.value == '*':
        #         value.value = int(val1) * int(val2)
        #     elif value.value == '/':
        #         value.value = int(val1) / int(val2)
        #     elif value.value == '<':
        #         value.value = int(val1) < int(val2)
        #     elif value.value == '>':
        #         value.value = int(val1) > int(val2)
        #     elif value.value == '%':
        #         value.value = int(val1) % int(val2)
        #     elif value.value == '==':
        #         value.value = int(val1) == int(val2)
        #     elif value.value == '&&':
        #         value.value = int(val1) and int(val2)
        #     elif value.value == '||':
        #         value.value = int(val1) or int(val2)
        #     elif value.value == '>=':
        #         value.value = int(val1) >= int(val2)
        #     elif value.value == '<=':
        #         value.value = int(val1) <= int(val2)
        #     elif value.value == '!=':
        #         value.value = int(val1) != int(val2)
        #     else:
        #         value.value = None
        #
        #     print(coloredDef("NEW"), value.value, value.name)
        #
        #     # else:
        #     #     for child in value.children:
        #     #         self.visitBop(child)
        #
        # print(coloredDef("BOP"), value.value, value.name)

    def visitUnaryOp(self, value: UnaryOpNode):
        print(coloredDef("UOP"), value.value, value.name)

    def visitRelationalOp(self, value: RelationalOpNode):
        print(coloredDef("ROP"), value.value, value.name)

