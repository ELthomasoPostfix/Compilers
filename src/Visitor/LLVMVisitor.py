from src.Nodes.LiteralNodes import promote, coerce
from src.Visitor.ASTreeVisitor import ASTreeVisitor, ForexpressionNode
from src.Nodes.ASTreeNode import *
from src.CompilersUtils import coloredDef


class Utils(enumerate):
    align = "align"
    i32 = "i32"
    alloca = "alloca"



class LLVMVisitor(ASTreeVisitor):
    def __init__(self):
        self.instructions = []

    def visitLiteral(self, node: LiteralNode):
        output_string = ""
        output_string += "%" + node.parent.children[1].value + " = " + Utils.alloca + " " + Utils.i32 + ", " + Utils.align + " " + str(4)
        output_string += '\n'
        output_string += "store i32 " + str(node.value) + ", i32* %" + node.parent.children[1].value + ", align 4"
        output_string += '\n'
        self.instructions.append(output_string)

    def visitBinaryop(self, node: ASTree):
        pass
        # self.instructions.append("Hey")

    def visitStatement(self, node: StatementNode):
        a = 5

    def visitExpression(self, node: ExpressionNode):
        a = 5

    # def visit

