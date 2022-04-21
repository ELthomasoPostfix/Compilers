from src.Nodes.JumpNodes import ReturnNode
from src.Nodes.LiteralNodes import *
from src.Visitor.ASTreeVisitor import ASTreeVisitor, ForexpressionNode, AssignmentNode, FunctiondeclaratorNode
from src.Nodes.ASTreeNode import *
from src.CompilersUtils import coloredDef


class LLVMVisitor(ASTreeVisitor):
    def __init__(self):
        self.instructions = []
        self.reg = '%'
        self.alloca = "alloca"
        self.tab = '\t'
        self.registerCounter = 0

#TODO: FUUUUUUUCKINGGGGGGGGGGGG lelijk maar had geen zin om een mooiere manier te zoeken x
    def returnTypeString(self, var_value):
        if isinstance(var_value, Record):
            if var_value.type.typeIndex == 2:
                return "i32"
            elif var_value.type.typeIndex == 3:
                return "float"
        if isinstance(var_value, IdentifierNode):
            if var_value.record.type.typeIndex == 1 or var_value.record.type.typeIndex == 2:
                return "i32"
            elif var_value.record.type.typeIndex == 3:
                return "float"
        if isinstance(var_value, TypedeclarationNode):
            if var_value.value == "int":
                return "i32"
            elif var_value.value == "float":
                return "float"
            # if var_value.
        if isinstance(var_value, IntegerNode):
            return "i32"
        elif isinstance(var_value, FloatNode):
            return "float"
        elif isinstance(var_value, CharNode):
            return ""

    def returnStatement(self, node, var_value):
        output_string = ""
        if isinstance(node.children[0], IdentifierNode):
            output_string += '\t' + "%" + str(self.registerCounter) + " = load " + var_value + ", " + var_value + "* %"
            output_string += node.children[0].value + ", align 4" + '\n'
            output_string += '\t' + "ret " + var_value + " %" + str(self.registerCounter) + '\n'
        else:
            output_string = '\t' + "ret " + var_value + " " + str(node.children[0].value) + '\n'
        # a = 5
        # output_string = '\t' + "ret " + var_value + " " + str(node.children[2].children[-1].children[0].value) + '\n'
        output_string += '}' + '\n' + '\n'
        return output_string

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        output_string = ""
        var_value = self.returnTypeString(node.children[0])
        output_string += "define " + var_value + " @" + node.children[1].value + "("
        for mapName, mapType in node.symbolTable.mapping.items():
            arg_value = self.returnTypeString(mapType)
            output_string += arg_value + " %"
            output_string += mapName
            output_string += ", "
        if len(node.symbolTable.mapping) != 0:
            output_string = output_string[:-2]
        output_string += ") #0 {" + '\n' + "entry:" + '\n'
        for mapName, mapType in node.symbolTable.mapping.items():
            output_string += '\t' + "%" + mapName + ".addr = alloca i32, align 4" + '\n'
            output_string += '\t' + "store " + var_value + " %" + mapName + ", " + var_value + "* %"
            output_string += mapName + ".addr, align 4" + '\n'
        self.instructions.append(output_string)
        self.visitChildren(node.children[2])
        if isinstance(node.children[2].children[-1], ReturnNode):
            output_string = self.returnStatement(node.children[2].children[-1],var_value)
        self.instructions.append(output_string)

    def visitVar_assig(self, node: Var_assigNode):
        output_string = ""
        isGlobal = False
        var_value = self.returnTypeString(node.children[1])
        if node.parent.symbolTable.isGlobal(node.children[0].value):
            self.tab = ''
            output_string += "@" + node.children[0].value + " = global " + var_value + " "
            output_string += node.children[1].value + ", align 4 "
            isGlobal = True
        else:
            output_string += self.tab + self.reg + node.children[0].value
            output_string += " = " + self.alloca + " " + str(var_value) + ", " + "align" + " " + str(4)
        output_string += '\n'
        self.instructions.append(output_string)
        output_string = self.tab
        if isinstance(node.children[1], IdentifierNode) and isGlobal is False:
            output_string += "%" + str(self.registerCounter) + " = " + "load " + str(var_value) + ", " + str(var_value) + "* %" + node.children[1].value
            output_string += ", align 4" + '\n' + self.tab
            output_string += "store " + str(var_value) + " %" + str(self.registerCounter) + ", " + str(var_value) + "* %" + node.children[0].value + ", align 4"
            output_string += '\n'
            self.instructions.append(output_string)
            self.registerCounter += 1
        elif isinstance(node.children[1], FunctioncallNode):
            output_string += "%call = call " + "i32" + " @" + node.children[1].value + '\n'
            output_string += '\t' + "store " + "i32" + " %call, " + "i32" + "* %" + node.children[0].value + ", align 4" + '\n'
            self.instructions.append(output_string)
        else:
            output_string += "store " + var_value + " " + str(node.children[1].value) + ", " + var_value
            output_string += "* %" + node.children[0].value + ", align 4"
            output_string += '\n'
            self.instructions.append(output_string)
