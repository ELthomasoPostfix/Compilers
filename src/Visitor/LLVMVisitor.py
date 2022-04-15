from src.Nodes.LiteralNodes import promote, coerce, IntegerNode
from src.Visitor.ASTreeVisitor import ASTreeVisitor, ForexpressionNode, AssignmentNode
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

    def visitIdentifier(self, node: IdentifierNode):
        output_string = ""
        if len(node.parent.parent.children) == 3:
            output_string += "%" + node.value
            output_string += " = " + Utils.alloca + " " + Utils.i32 + ", " + Utils.align + " " + str(4)
            output_string += '\n'
            self.instructions.append(output_string)
            output_string = ""
            if isinstance(node.parent.parent.children[2], IdentifierNode):
                output_string += "%0 = " + "load i32, i32* %" + node.parent.parent.children[2].value
                output_string += ", align 4" + '\n'
                output_string += "store i32 %0, i32* %" + node.value + ", align 4" + '\n'
                self.instructions.append(output_string)



