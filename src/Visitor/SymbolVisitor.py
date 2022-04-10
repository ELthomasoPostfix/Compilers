from src.SymbolTable import SymbolTable, ReadAccess, ReadWriteAccess, Record, VariableCType, FunctionCType, CType
from src.Visitor.ASTreeVisitor import ASTreeVisitor, CompoundstatementNode
from src.Nodes.ASTreeNode import *


class SymbolVisitor(ASTreeVisitor):
    def __init__(self, globalSymbolTable: SymbolTable):
        self.currentSymbolTable = globalSymbolTable

    #
    # HELPER METHODS
    #

    def _createScope(self):
        """Attach a new SymbolTable to the current one. Make the new SymbolTable the current one"""
        self.currentSymbolTable = SymbolTable(self.currentSymbolTable, self.currentSymbolTable.typeList)
    
    def _closeScope(self):
        """Make the enclosing SymbolTable the current one."""
        self.currentSymbolTable = self.currentSymbolTable.enclosingScope

    def _enterNewSubScope(self, node: ScopedNode):
        """
        For :node: and its children, work in the context of a new sub scope.
        It is implicitly assumed that the :node: argument is a ScopedNode,
        such that it requires a reference to the newly created SymbolTable.
        :param node: The node that generates a new scope, and so a new SymbolTable
        """
        self._createScope()
        self._attachSymbolTable(node)
        self.visitChildren(node)
        self._closeScope()

    def _attachSymbolTable(self, node: ScopedNode):
        node.symbolTable = self.currentSymbolTable

    def _attachRecord(self, node: TypedNode):
        record: Record = self.currentSymbolTable[node.value]
        if record is None:
            raise Exception(f"Unknown symbol: '{node.__repr__()}'")
        node.record = record

    #
    #   IGNORE SYNTACTIC SUGAR
    #

    def visitCfile(self, node: CfileNode):
        self.visitChildren(node)

    def visitStatement(self, node: StatementNode):
        self.visitChildren(node)

    def visitVar_assig(self, node: Var_assigNode):
        self.visitChildren(node)

    def visitExpression(self, node: ExpressionNode):
        self.visitChildren(node)

    def visitBinaryop(self, node: ASTree):
        self.visitChildren(node)

    def visitDeclarator(self, node: DeclaratorNode):
        self.visitChildren(node)

    def visitTypedeclaration(self, node: TypedeclarationNode):
        self.visitChildren(node)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        self.visitChildren(node)

    #
    #   SUB SCOPE CREATION
    #

    def visitBlock(self, node: BlockNode):
        self._enterNewSubScope(node)
        self.visitChildren(node)

    def visitCompoundstatement(self, node: CompoundstatementNode):
        self._enterNewSubScope(node)

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self._enterNewSubScope(node)

    def visitIterationstatement(self, node: IterationstatementNode):
        self._enterNewSubScope(node)

    #
    #   SYMBOL DECLARATIONS
    #

    def visitVar_decl(self, node: Var_declNode):
        identifier: str = node.getChild(1).children[-1].value
        access = ReadWriteAccess()
        typeName = ""

        for typeInfo in node.getChild(0).children:
            if isinstance(typeInfo, TypequalifierNode):
                access = ReadAccess()
            else:
                typeName += typeInfo.value

        varType: CType = VariableCType(self.currentSymbolTable.typeList[typeName])
        for child in node.getChild(1).children:
            if isinstance(child, PointerNode):
                varType.addPointer(len(child.children) == 1)

        self.currentSymbolTable[identifier] = Record(varType, access)
        self.visitChildren(node)

    #
    #   SYMBOL UTILISATION
    #

    def visitIdentifier(self, node: IdentifierNode):
        self._attachRecord(node)
