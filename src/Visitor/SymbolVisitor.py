from src.SymbolTable import SymbolTable, ReadAccess, ReadWriteAccess, TypeList
from src.Visitor.ASTreeVisitor import ASTreeVisitor
from src.Nodes.ASTreeNode import *


class OptimizationVisitor(ASTreeVisitor):
    def __init__(self, globalSymbolTable: SymbolTable, typeList: TypeList):
        self.currentSymbolTable = globalSymbolTable
        self.typeList = typeList

    def visitCfile(self, node: CfileNode):
        self.visitChildren(node)

    def visitBlock(self, node: BlockNode):
        self.visitChildren(node)

    def visitStatement(self, node: StatementNode):
        self.visitChildren(node)

    def visitExpression(self, node: ExpressionNode):
        self.visitChildren(node)

    def visitVar_decl(self, node: Var_declNode):
        identifier = None
        access = ReadWriteAccess()
        typeName = ""

        for child in node.getChild(1).children:
            if isinstance(child, IdentifierNode):
                identifier = child.name
                break

        for typeInfo in node.getChild(0).children:
            if isinstance(typeInfo, TypequalifierNode):
                access = ReadAccess()
            else:
                typeName += typeInfo.name

            self.currentSymbolTable[identifier] = [self.typeList[typeName], access]
