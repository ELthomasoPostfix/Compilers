from __future__ import annotations

from typing import Tuple

from src.CompilersUtils import coloredDef
from src.Exceptions.exceptions import UnknownType, UnsupportedFeature, InvalidBinaryOperation
from src.Nodes.IterationNodes import WhileNode
from src.Nodes.JumpNodes import *
from src.Nodes.LiteralNodes import *
from src.Nodes.SelectionNodes import IfNode, ElseNode
from src.SymbolTable import FunctionCType
from src.Visitor.ASTreeVisitor import ASTreeVisitor, ForexpressionNode, AssignmentNode, FunctiondeclaratorNode
from src.Nodes.ASTreeNode import *
from src.Enumerations import LLVMKeywords as llk
from src.Visitor.GenerationVisitor import GenerationVisitor


class LLVMVisitor(GenerationVisitor):
    def __init__(self, typeList: TypeList):
        self.instructions = []
        self.tab = '\t'
        self.localRegisterCounter = 0
        self.globalRegisterCounter = 0
        self.thenCounter = 0
        self.elseCounter = 0
        self.endCounter = 0
        self.labelCounter = 0
        super().__init__(typeList)

    #
    #   REGISTER HANDLING HELPER METHODS
    #
    def _reserveUnnamedRegister(self, prefix: str) -> str:
        if prefix == "%":
            reservedReg: str = f"%{self.localRegisterCounter}"
            self._incrLocalRegCtr()
            return reservedReg
        elif prefix == "@":
            reservedReg: str = f"@{self.globalRegisterCounter}"
            self._incrGlobalRegCtr()
            return reservedReg
        else:
            raise Exception(
                f"unknown unnamed temporary prefix: '{prefix}' when trying to reserve unnamed temporary register")

    def _incrGlobalRegCtr(self):
        self.globalRegisterCounter += 1

    def _incrLocalRegCtr(self):
        self.localRegisterCounter += 1

    def _resetLocalRegCtr(self):
        self.localRegisterCounter = 0

    def _getNamedRegisterPrefix(self, symbol: str):
        if self.currentSymbolTable.isGlobal(symbol):
            return "@"
        else:
            return "%"

    def _getExpressionLocation(self, expression: ExpressionNode) -> str:
        """
        After evaluation of an expression, its result is stored in some
        location. This method determines the location of that result.
        Nodes that may be passed are: IdentifierNode, any LiteralNode,
        FunctioncallNode, BinaryopNode, UnaryexpressionNode and UnaryopNode.
        These classes all have ExpressionNode as a super class.

        Note that for FunctioncallNode, BinaryopNode, UnaryexpressionNode and
        UnaryopNode the location can only be determined with certainty immediately
        after they have been evaluated (== accept(LLVMVisitor) has been called on them).

        :param expression: The expression to determine the location of
        :return: The location
        """

        if isinstance(expression, LiteralNode):
            value = str(expression.getValue())

            # If Literal not part of an expression, store it in an intermediate register
            if not expression.hasTypeAncestor(ExpressionNode):
                sumKeyword = llk.SUM
                literalLLVMtype = self._CToLLVMType(expression.inferType(self.typeList))
                sumKeyword = self._getBinaryOpPrefix(sumKeyword, literalLLVMtype) + sumKeyword
                dstRegister = self._reserveUnnamedRegister('%')

                intermediateInstr = '\t' + f"{dstRegister} = {sumKeyword} {literalLLVMtype} 0, {value}" + '\n'
                self.instructions.append(intermediateInstr)
                value = dstRegister

            return value
        elif isinstance(expression, IdentifierNode):
            NamedRegister = self.currentSymbolTable[expression.identifier].register

            # Variable declarations result in a named register
            # Any use of a declared variable will permanently move
            # the value of the named register into an unnamed one
            if not NamedRegister[1:].isnumeric():
                UnnamedRegister = self._reserveUnnamedRegister(NamedRegister[0])
                NamedRegType = self._CToLLVMType(
                    expression.getType()) + "*"  # TODO implicit address-of operator should take care of this???
                self.instructions.append(
                    self._createLoadStatement(NamedRegType, NamedRegister, NamedRegType[:-1], UnnamedRegister,
                                              wrap=True))

                self.currentSymbolTable[expression.identifier].register = UnnamedRegister

            # Always returns an unnamed register
            return self.currentSymbolTable[expression.identifier].register
        # The location an expression would be stored in
        elif isinstance(expression, Var_assigNode):
            return self.currentSymbolTable[expression.getIdentifierNode().identifier].register
        else:
            return f"%{self.localRegisterCounter - 1}"

    def _evaluateExpression(self, expressionNode: ExpressionNode) -> str:
        expressionNode.accept(self)
        return self._getExpressionLocation(expressionNode)

    #
    #   SCOPE HANDLING HELPER METHODS
    #

    def _openScope(self, node: ScopedNode):
        """Access the passed node to change the current scope to the scope it represents."""
        self.currentSymbolTable = node.symbolTable

    def _closeScope(self):
        """Make the enclosing SymbolTable the current one."""
        self.currentSymbolTable = self.currentSymbolTable.enclosingScope

    #
    #   HELPER METHODS
    #

    def _createStoreStatement(self, paramType: str, paramLoc, dstType: str, dstLoc: str, wrap: bool = False):
        """
        Create a LLVM store statement using the passed parameters.

        :param paramType: The LLVM type of the to store value
        :param paramLoc: The LLVM literal value in case of a Literal and the LLVM named/unnamed register in case of an expression or identifier
        :param dstType: The LLVM type of the memory to store into
        :param dstLoc: The LLVM memory to store into. Should be of pointer type
        :param wrap: Whether or not to wrap the store statement in a '\t' prefix and '\n' postfix
        :return: The LLVM store statement in string format
        """

        storeStmt = f"{llk.STORE} {paramType} {paramLoc}, {dstType} {dstLoc}"
        if wrap: storeStmt = '\t' + storeStmt + '\n'
        return storeStmt

    def _createLoadStatement(self, srcType: str, srcLoc, dstType: str, dstLoc: str, wrap: bool = False):
        """
        Create a LLVM load statement using the passed parameters.

        :param srcType: The LLVM pointer type of the to load from memory location
        :param srcLoc: The LLVM to load from memory location
        :param dstType: The LLVM type of the register to load into
        :param dstLoc: The LLVM of the register to load into
        :param wrap: Whether or not to wrap the store statement in a '\t' prefix and '\n' postfix
        :return: The LLVM store statement in string format
        """

        loadStmt = f"{dstLoc} = {llk.LOAD} {dstType}, {srcType} {srcLoc}"
        if wrap: loadStmt = '\t' + loadStmt + '\n'
        return loadStmt

    def _getBinaryOpPrefix(self, binaryOpInstruction: str, operandLLVMType: str):
        prefix = ""
        binaryOpInstruction = binaryOpInstruction[:3]
        if operandLLVMType == llk.FLOAT:
            prefixedOps = [llk.SUM, llk.MIN, llk.MUL, llk.DIV, llk.MOD, llk.COMPARE]
            if binaryOpInstruction in prefixedOps:
                prefix = llk.FOP_PREF

        if operandLLVMType == llk.I32:
            prefixedOps = [llk.DIV, llk.MOD]
            if binaryOpInstruction in prefixedOps:
                prefix = llk.SOP_PREF

            prefixedOps = [llk.COMPARE]
            if binaryOpInstruction in prefixedOps:
                prefix = llk.IOP_PREF

        return prefix

    def _CToLLVMType(self, cType: CType) -> str:
        # TODO take array type into account
        llvmType = ""
        if cType == self.typeList[BuiltinNames.CHAR]:
            llvmType = LLVMKeywords.CHAR
        elif cType == self.typeList[BuiltinNames.INT]:
            llvmType = LLVMKeywords.I32
        elif cType == self.typeList[BuiltinNames.FLOAT]:
            llvmType = LLVMKeywords.FLOAT
        elif cType == self.typeList[BuiltinNames.VOID]:
            llvmType = LLVMKeywords.VOID

        return llvmType + "*" * cType.pointerCount()

    def returnTypeString(self, expressionNode) -> str:
        """
        Return the LLVM type keyword for the given node from which
        a type can be inferred. Nodes that may be passed are: IdentifierNode,
        any LiteralNode, FunctioncallNode, BinaryopNode, UnaryexpressionNode
        and UnaryopNode

        :param expressionNode: The node from which a CType may be inferred, i.e. a node possessing the method inferType(TypeList)
        :return: The LLVM type corresponding to the CType of :var_value: as a string
        """

        cType: CType | str = expressionNode.inferType(self.typeList)
        llvmType = self._CToLLVMType(cType)

        return llvmType

    def returnStatement(self, returnNode: JumpstatementNode, returnType: str):
        if returnType == llk.VOID:
            return '\t' + f"{llk.RETURN} {returnType}" + '\n'

        output_string = ""
        returnExpression = returnNode.getChild(0)

        retExpLocation = self._evaluateExpression(returnExpression)  # evaluate return expression
        retExpType = self._CToLLVMType(returnExpression.inferType(self.typeList))

        return '\t' + f"{llk.RETURN} {retExpType} {retExpLocation}" + '\n'

    #
    #   VISITOR METHODS
    #

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        # update scope
        self._openScope(node)

        # Unnamed register counter works on a per-function basis
        self._resetLocalRegCtr()

        output_string = ""
        identifierNode = node.getIdentifierNode()
        retType = self.returnTypeString(identifierNode)  # the LLVM type of the return type

        output_string += f"{llk.DEFINE} {retType} @{identifierNode.identifier}("

        allocations = []
        stores = []

        # Add parameter declarations
        paramIdentifiers = node.getParamIdentifierNodes()
        for pId in paramIdentifiers:
            paramType = self.returnTypeString(pId)
            output_string += f"{paramType} %{pId.identifier}"

            idName = pId.identifier
            registerPrefix = self._getNamedRegisterPrefix(idName)
            cpyRegister = f"{registerPrefix}{idName}.addr"
            allocations.append('\t' + f"{cpyRegister} = {llk.ALLOCA} {paramType}" + '\n')
            stores.append(self._createStoreStatement(
                paramType, registerPrefix + idName,
                           paramType + '*', cpyRegister,
                # TODO  the '*' should be done through implicit address-of operator for the right side of a assignment
                wrap=True))
            self.currentSymbolTable[idName].register = cpyRegister

            # Check object identity, not equality (mem address vs __eq__ method)
            if pId is not paramIdentifiers[-1]:
                output_string += ", "

        # Add parameter allocations and copying
        output_string += ") {" + '\n' + "entry:" + '\n'
        output_string += "".join(allocations)
        output_string += "".join(stores)

        self.instructions.append(output_string)

        # Visit compound statement
        node.getChild(2).accept(self)

        # Append function closing bracket
        self.instructions.append('}' + '\n' + '\n')

        # update scope
        self._closeScope()

    # TODO  Give NoneType exception for Input/tests/functions.txt if super().visitFunctiondeclaration() is used instead.
    def visitFunctiondeclaration(self, node: FunctiondeclarationNode):
        pass

    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    def visitVariabledeclaration(self, node: VariabledeclarationNode):
        identifierNode = node.getIdentifierNode()
        idLLVMType = self._CToLLVMType(identifierNode.getType())
        identifier = node.getIdentifierNode().identifier
        allocInstr = ""
        dstLocation = self._getNamedRegisterPrefix(identifier) + identifier

        # TODO  global vars are scuffer, also see self.visitVar_assig()
        if dstLocation[0] == '@':
            initValue = 0

            rightSibling = node.parent.getChild(node.parent.children.index(node) + 1)
            if rightSibling is not None and isinstance(rightSibling, Var_assigNode) and \
                    rightSibling.getIdentifierNode().identifier == identifier and \
                    isinstance(rightSibling.getChild(1), LiteralNode):
                initValue = rightSibling.getChild(1).getValue()
                idLLVMType = self._CToLLVMType(rightSibling.getChild(1).inferType(self.typeList))

            allocInstr = f"{dstLocation} = global {idLLVMType} {initValue}" + '\n'
        else:
            allocInstr = '\t' + f"{dstLocation} = {llk.ALLOCA} {idLLVMType}" + '\n'

        self.currentSymbolTable[identifier].register = dstLocation
        self.instructions.append(allocInstr)

    # TODO  for global variables,
    # TODO      int a;
    # TODO      a = 2;
    # TODO  is not actually valid C code??? definition on same line?
    def visitVar_assig(self, node: Var_assigNode):

        # TODO this is a scuffed fix: Ignore global var initialization assignments,
        #   let visitVariabledeclaration handle those
        if self.currentSymbolTable is None:
            return

        lhs = node.getChild(0)
        rhs = node.getChild(1)

        # Visit rhs expression
        rhsLocation = self._evaluateExpression(rhs)

        if not isinstance(lhs, IdentifierNode):
            raise UnsupportedFeature("The left hand side of an assignment MUST be an identifier for now")

        # Visit lhs expression
        lhs.accept(self)

        # Assign the register where the result is stored as the location of lhs
        self.currentSymbolTable[lhs.identifier].register = rhsLocation

        # TODO if lhs is an expression (ptr type?), then do a store
        #  output_string = self._createStoreStatement(rhsLLVMType, rhsLocation, lhsLLVMType, lhsLocation, wrap=True)
        #  self.instructions.append(output_string)

    def visitBinaryop(self, node: BinaryopNode):

        lhs: ExpressionNode = node.getChild(0)
        rhs: ExpressionNode = node.getChild(1)
        lhsLLVMType = self._CToLLVMType(lhs.inferType(self.typeList))

        # evaluate lhs
        lhsLocation = self._evaluateExpression(lhs)

        # evaluate rhs
        rhsLocation = self._evaluateExpression(rhs)

        # Reserve register only after operands have reserved theirs
        dstTempRegister: str = self._reserveUnnamedRegister('%')

        binaryOpInstruction = node.getLLVMOpKeyword()
        binaryOpInstruction = self._getBinaryOpPrefix(binaryOpInstruction, lhsLLVMType) + binaryOpInstruction

        output_string = '\t' + \
                        f"{dstTempRegister} = {binaryOpInstruction} {lhsLLVMType} {lhsLocation}, {rhsLocation}" + \
                        '\n'
        self.instructions.append(output_string)

    def visitFunctioncall(self, node: FunctioncallNode):
        # TODO
        # TODO
        # TODO
        # TODO  LLVM supports calling C library functions such as printf and scanf, so just call those !!!!!!!!
        # TODO
        # TODO
        # TODO

        output_string = ""
        identifierNode = node.getIdentifierNode()

        dstTempRegister: str = self._reserveUnnamedRegister('%')
        identifier = identifierNode.identifier
        retType = self.returnTypeString(identifierNode)
        callParams = node.getParameterNodes()

        output_string += '\t' + f"{dstTempRegister} = {llk.CALL} {retType} @{identifier} ("

        for idx, param in enumerate(callParams):
            # Evaluate the parameter expression
            paramLoc = self._evaluateExpression(param)

            # Add expression result to call
            output_string += f"{self._CToLLVMType(param.inferType(self.typeList))} {paramLoc}"

            # Add comma separator
            # Check object identity, not equality (mem address vs __eq__ method)
            if param is not callParams[-1]:
                output_string += ", "

        output_string += ")" + '\n'

        self.instructions.append(output_string)

    def visitJumpstatement(self, node: JumpstatementNode):
        if isinstance(node, ReturnNode):
            funcDefType = node.getAncestorOfType(FunctiondefinitionNode).getIdentifierNode().getType()
            output_string = self.returnStatement(node, self._CToLLVMType(funcDefType))
            self.instructions.append(output_string)
        if isinstance(node, ContinueNode):
            a = 5
            pass

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self._openScope(node)
        while True:
            elseCheck = False
            baseIdx, endIdx = 0, len(node.children)
            if isinstance(node, IfNode):
                result = self._evaluateExpression(node.getChild(0))
            if isinstance(node, IfNode):
                if isinstance(node.getChild(-1), ElseNode):
                    elseCheck = True
                if elseCheck:
                    self.instructions.append('\t' + f"{llk.BRANCH} {llk.I1} {result}, label %if.then{self.thenCounter}, " \
                                                    f"label %if.else{self.elseCounter}" + '\n')
                else:
                    self.instructions.append('\t' + f"{llk.BRANCH} {llk.I1} {result}, label %if.then{self.thenCounter}, " \
                                                    f"label %if.end{self.endCounter}" + '\n')
                self.instructions.append('\n' + f"if.then{self.thenCounter}:" + '\n')
                self.thenCounter += 1

                baseIdx = 1
                endIdx -= 1

            for i in range(baseIdx, endIdx):
                node.children[i].accept(self)

            self.instructions.append('\t' + f"br label %if.end{self.endCounter}" + '\n')
            if elseCheck:
                self.instructions.append('\n' + f"if.else{self.elseCounter}:" + '\n')
                self.elseCounter += 1
                node = node.getChild(-1)
            else:
                self.instructions.append('\n' + f"if.end{self.endCounter}:" + '\n')
                self.endCounter += 1
                break
        self._closeScope()

    def visitIterationstatement(self, node: IterationstatementNode):
        self._openScope(node)

        output_string = ""
        ifn = node
        result = self._evaluateExpression(ifn.getChild(0))
        output_string += '\t' + f"br label %while.cond{self.labelCounter}" + '\n'
        output_string += '\n' + f"while.cond{self.labelCounter}:" + '\n'
        output_string += '\t' + f"br i1 {result}, label %while.body{self.labelCounter}, label %while.end{self.labelCounter}"
        output_string += '\n' + '\n'
        output_string += f"while.body{self.labelCounter}:" + '\n'
        self.instructions.append(output_string)
        for i in range(1, len(node.children)):
            node.children[i].accept(self)
        self.instructions.append('\n' + f"while.end{self.labelCounter}:" + '\n')
        self.labelCounter += 1
        self._closeScope()

    #
    #   NON-LLVM-GENERATING VISITOR METHODS
    #

    def visitLiteral(self, node: LiteralNode):
        # Literals should be accessed directly through the AST
        pass

    def visitIdentifier(self, node: IdentifierNode):
        # Identifiers must be components of instructions
        pass
