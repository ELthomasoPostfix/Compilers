from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import *
from src.CompilersUtils import coloredDef


class OptimizationVisitor:
    def visitExp(self, exp: ExpNode):
        print(coloredDef("EXP"), exp.value, exp.name)

    def visitValueExp(self, value: ValueExpNode):
        print(coloredDef("VEXP"), value.value, value.name)

    def visitValue(self, value: ValueNode):
        print(coloredDef("VAL"), value.value, value.name)

    def visitBop(self, value: BopNode):
        print(coloredDef("BOP"), value.value, value.name)
