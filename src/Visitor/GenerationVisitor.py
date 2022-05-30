from __future__ import annotations

from src.Nodes.ASTreeNode import BlockNode, ScopedNode, CompoundstatementNode, FunctiondeclarationNode
from src.SymbolTable import TypeList, SymbolTable
from src.Visitor.ASTreeVisitor import ASTreeVisitor


class GenerationVisitor(ASTreeVisitor):
    def __init__(self, typeList: TypeList):
        self.typeList: TypeList = typeList
        self.currentSymbolTable: SymbolTable | None = None
        super().__init__()

    def _openScope(self, node: ScopedNode):
        """Access the passed node to change the current scope to the scope it represents."""
        self.currentSymbolTable = node.symbolTable

    def _closeScope(self):
        """Make the enclosing SymbolTable the current one."""
        self.currentSymbolTable = self.currentSymbolTable.enclosingScope

    def visitBlock(self, node: BlockNode):
        self._openScope(node)

        # The self.visitChildren(node) call may be replaced by target generation code
        self.visitChildren(node)

        self._closeScope()

    def visitCompoundstatement(self, node: CompoundstatementNode):
        self._openScope(node)

        # The self.visitChildren(node) call may be replaced by target generation code
        self.visitChildren(node)

        self._closeScope()

    def visitFunctiondeclaration(self, node: FunctiondeclarationNode):
        pass
