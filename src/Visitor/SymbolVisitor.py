from src.SymbolTable import SymbolTable, ReadAccess, ReadWriteAccess, TypeList
from src.Visitor.ASTreeVisitor import ASTreeVisitor, CompoundstatementNode
from src.Nodes.ASTreeNode import *


class SymbolVisitor(ASTreeVisitor):
    def __init__(self, globalSymbolTable: SymbolTable):
        self.currentSymbolTable = globalSymbolTable

    #
    # HELPER METHODS
    #

    def createScope(self):
        self.currentSymbolTable = SymbolTable(self.currentSymbolTable, self.currentSymbolTable.typeList)
    
    def closeScope(self):
        self.currentSymbolTable = self.currentSymbolTable.enclosingScope

    def enterNewSubScope(self, node: ASTree):
        """For :node: and its children, work in the context of a new sub scope."""
        self.createScope()
        self.visitChildren(node)
        self.closeScope()

    #
    #   IGNORE SYNTACTIC SUGAR
    #

    def visitCfile(self, node: CfileNode):
        self.visitChildren(node)

    def visitBlock(self, node: BlockNode):
        self.visitChildren(node)

    def visitStatement(self, node: StatementNode):
        self.visitChildren(node)

    def visitVar_assig(self, node: Var_assigNode):
        self.visitChildren(node)

    def visitExpression(self, node: ExpressionNode):
        self.visitChildren(node)

    def visitBinaryop(self, node: ASTree):
        self.visitChildren(node)

    #
    #   SUB SCOPE CREATION
    #

    def visitCompoundstatement(self, node: CompoundstatementNode):
        self.enterNewSubScope(node)

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self.enterNewSubScope(node)

    def visitIterationstatement(self, node: IterationstatementNode):
        self.enterNewSubScope(node)

    #
    #   SYMBOL DECLARATIONS
    #

    def visitVar_decl(self, node: Var_declNode):
        identifier = None
        access = ReadWriteAccess()
        typeName = ""

        for child in node.getChild(1).children:
            if isinstance(child, IdentifierNode):
                identifier = child.value
                break

        for typeInfo in node.getChild(0).children:
            if isinstance(typeInfo, TypequalifierNode):
                access = ReadAccess()
            else:
                typeName += typeInfo.value

        self.currentSymbolTable[identifier] = [self.currentSymbolTable.typeList[typeName], access]

    #
    #   SYMBOL UTILISATION
    #

    def visitIdentifier(self, node: IdentifierNode):
        if self.currentSymbolTable[node.value] is None:
            raise Exception(f"Unknown symbol: '{node.__repr__()}'")
