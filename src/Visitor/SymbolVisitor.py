from __future__ import annotations

from typing import Tuple, Callable

from src.CompilersUtils import first
from src.Exceptions.exceptions import UndeclaredSymbolException
from src.SymbolTable import SymbolTable, Record, Accessibility, ReadAccess,\
    ReadWriteAccess, CType, VariableCType, FunctionCType
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

    def _enterNewSubScope(self, node: ScopedNode, ):
        """
        For :node: and its children, work in the context of a new sub scope.
        It is implicitly assumed that the :node: argument is a ScopedNode,
        such that it requires a reference to the newly created SymbolTable.

        :param node: The node that generates a new scope, and so a new SymbolTable
        :param callback: A function to call after symbol table creation and before the children are recursively visited
        """
        self._createScope()
        self._attachSymbolTable(node)
        self.visitChildren(node)
        self._closeScope()

    def _attachSymbolTable(self, node: ScopedNode):
        node.symbolTable = self.currentSymbolTable

    def _attachRecord(self, node: TypedNode):
        record: Record = self.currentSymbolTable[node.value]
        if record is None:      # TODO  push this into a SemanticVisitor ???
            raise UndeclaredSymbolException(node.value)
        node.record = record

    def _determineCTypeInfo(self, node: TypedeclarationNode) -> Tuple[str, Accessibility]:
        access: Accessibility = ReadWriteAccess()
        typeName: str = ""
        for typeInfo in node.children:
            if isinstance(typeInfo, TypequalifierNode):
                access = ReadAccess()
            else:
                typeName += typeInfo.value

        return typeName, access

    def _determineVariableCType(self, node: Var_declNode) -> Tuple[VariableCType, Accessibility]:
        typeName, access = self._determineCTypeInfo(node.getChild(0))

        varType: VariableCType = VariableCType(self.currentSymbolTable.typeList[typeName])
        self._addPointerTypeInfo(node.getChild(1), varType)

        return varType, access

    def _addPointerTypeInfo(self, node: DeclaratorNode, type: CType) -> None:
        for child in node.children:
            if isinstance(child, PointerNode):
                type.addPointer(len(child.children) == 1)

    def _determineVariableRecord(self, node: Var_declNode) -> Tuple[str, Record]:
        identifier: str = node.getIdentifierNode().value
        varType, access = self._determineVariableCType(node)

        return identifier, Record(varType, access)

    def _determineFunctionPartialRecord(self, node: FunctiondeclarationNode | FunctiondefinitionNode) -> Tuple[str, Record]:
        identifier: str = node.getIdentifierNode().value
        typeName, access = self._determineCTypeInfo(node.getChild(0))
        access = ReadAccess()

        varType: FunctionCType = FunctionCType(self.currentSymbolTable.typeList[typeName])
        self._addPointerTypeInfo(node.getChild(1), varType)

        return identifier, Record(varType, access)

    def _determineFunctionSymbols(self, node: FunctiondeclarationNode | FunctiondefinitionNode) -> None:
        identifier, record = self._determineFunctionPartialRecord(node)
        self.currentSymbolTable[identifier] = record

        self._enterNewSubScope(node)

        for parameter in node.getChild(1).children:
            if isinstance(parameter, Var_declNode):
                record.type.paramTypes.append(parameter.getIdentifierNode().record.type)


    #
    #   SUB SCOPE CREATION
    #

    def visitBlock(self, node: BlockNode):
        self._enterNewSubScope(node)

    def visitCompoundstatement(self, node: CompoundstatementNode):
        self._enterNewSubScope(node)

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self._enterNewSubScope(node)

    def visitIterationstatement(self, node: IterationstatementNode):
        self._enterNewSubScope(node)

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        self._determineFunctionSymbols(node)

    def visitFunctiondeclaration(self, node: FunctiondeclarationNode):
        self._determineFunctionSymbols(node)


    #
    #   SYMBOL DECLARATIONS
    #

    def visitVar_decl(self, node: Var_declNode):
        identifier, record = self._determineVariableRecord(node)
        self.currentSymbolTable[identifier] = record

        self.visitChildren(node)

    #
    #   SYMBOL UTILISATION
    #

    def visitIdentifier(self, node: IdentifierNode):
        self._attachRecord(node)
