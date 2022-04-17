from __future__ import annotations

from typing import Tuple, Callable

from src.CompilersUtils import first
from src.Exceptions.exceptions import UndeclaredSymbol
from src.SymbolTable import SymbolTable, Record, Accessibility, ReadAccess,\
    ReadWriteAccess, CType, VariableCType, FunctionCType
from src.Nodes.ASTreeNode import *


class SymbolVisitor(ASTreeVisitor):
    def __init__(self, typeList: TypeList):
        self.typeList: TypeList = typeList
        self.currentSymbolTable = None

    #
    # HELPER METHODS
    #

    def _createScope(self):
        """Attach a new SymbolTable to the current one. Make the new SymbolTable the current one"""
        self.currentSymbolTable = SymbolTable(self.currentSymbolTable, self.typeList)
    
    def _closeScope(self):
        """Make the enclosing SymbolTable the current one."""
        self.currentSymbolTable = self.currentSymbolTable._enclosingScope

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
        if record is None:      # TODO  push this into a SemanticVisitor ???
            raise UndeclaredSymbol(node.value)
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

        varType: VariableCType = VariableCType(self.typeList[typeName])
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

    def _determineDummyFunctionRecord(self, node: FunctiondeclarationNode | FunctiondefinitionNode) -> Tuple[str, Record]:
        identifier: str = node.getIdentifierNode().value
        typeName, access = self._determineCTypeInfo(node.getChild(0))
        access = ReadAccess()

        # Construct partial (parameterless) function type
        varType: FunctionCType = FunctionCType(self.typeList[typeName], isinstance(node, FunctiondefinitionNode))
        self._addPointerTypeInfo(node.getChild(1), varType)

        # Fill out dummy parameter info
        for parameter in node.getChild(1).children:
            if isinstance(parameter, Var_declNode):
                a = self._determineVariableRecord(parameter)
                varType.paramTypes.append(self._determineVariableRecord(parameter)[1].type)

        return identifier, Record(varType, access)

    def _registerDummyFunctionRecord(self, node: FunctiondeclarationNode | FunctiondefinitionNode) -> FunctionCType:
        identifier, record = self._determineDummyFunctionRecord(node)
        self.currentSymbolTable[identifier] = record

        return record.type

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
        functionType: FunctionCType = self._registerDummyFunctionRecord(node)

        self._enterNewSubScope(node)

        # Attach actual record references
        functionType.paramTypes.clear()
        for parameter in node.getChild(1).children:
            if isinstance(parameter, Var_declNode):
                functionType.paramTypes.append(parameter.getIdentifierNode().record.type)


    def visitFunctiondeclaration(self, node: FunctiondeclarationNode):
        self._registerDummyFunctionRecord(node)

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
