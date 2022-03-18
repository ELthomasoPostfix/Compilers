from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import *
from src.CompilersUtils import coloredDef


class OptimizationVisitor(ASTreeVisitor):
    def visitStatement(self, value: StatementNode):
        print(coloredDef("STAT"), value.value, value.name)

    def visitExpression(self, exp: ExpressionNode):
        print(coloredDef("EXP"), exp.value, exp.name)

    def visitLiteral(self, value: LiteralNode):
        print(coloredDef("VAL"), value.value, value.name)
    def visitBinaryop(self, value: BinaryopNode):
        if len(value.children) == 2:
            for child in value.children:
                if isinstance(child, BinaryopNode):
                    child.parent = value
                    self.visitBinaryop(child)
            if isinstance(value.children[0], LiteralNode) and isinstance(value.children[1], LiteralNode):
                child1 = int(value.children[0].value)
                child2 = int(value.children[1].value)
                val = value.evaluateLiterals([child1, child2])
                # value.name = "Li"
                # value.value = val
                value.children = []
                value.replaceSelf(LiteralNode(val, "Li", value.parent))





    def visitUnaryOp(self, value: UnaryopNode):
        print(coloredDef("UOP"), value.value, value.name)

    def visitRelationalOp(self, value: RelationalopNode):
        print(coloredDef("ROP"), value.value, value.name)

