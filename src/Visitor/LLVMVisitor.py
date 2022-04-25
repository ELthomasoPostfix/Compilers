from __future__ import annotations

from typing import Tuple

from src.CompilersUtils import coloredDef
from src.Exceptions.exceptions import UnknownType, UnsupportedFeature, InvalidBinaryOperation
from src.Nodes.IterationNodes import WhileNode
from src.Nodes.JumpNodes import ReturnNode
from src.Nodes.LiteralNodes import *
from src.Nodes.SelectionNodes import IfNode
from src.SymbolTable import FunctionCType
from src.Visitor.ASTreeVisitor import ASTreeVisitor, ForexpressionNode, AssignmentNode, FunctiondeclaratorNode
from src.Nodes.ASTreeNode import *
from src.Enumerations import LLVMKeywords as llk



class LLVMVisitor(ASTreeVisitor):
    def __init__(self, typeList: TypeList):
        self.instructions = []
        self.typeList = typeList
        self.tab = '\t'
        self.localRegisterCounter = 0
        self.globalRegisterCounter = 0
        self.currentSymbolTable: SymbolTable | None = None
        self.labelCounter = 0

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
            raise f"unknown unnamed temporary prefix: {prefix} when trying to reserve unnamed temporary register"

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
            return str(expression.getValue())
        elif isinstance(expression, IdentifierNode):

            if False:
                srcLocation = self.currentSymbolTable[expression.identifier].register
                if not srcLocation[1:].isnumeric():
                    dstLocation = self._reserveUnnamedRegister(srcLocation[0])
                    srcType = self._CToLLVMType(expression.getType()) + "*"     # TODO implicit address-of operator should take care of this???
                    self.instructions.append(self._createLoadStatement(srcType, srcLocation, srcType[:-1], dstLocation))
            return f"{self._getNamedRegisterPrefix(expression.identifier)}{expression.identifier}"
        # The location an expression would be stored in
        elif isinstance(expression, Var_assigNode):
            return self.currentSymbolTable[expression.getIdentifierNode().identifier].register
        else:
            return f"%{self.localRegisterCounter - 1}"

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
            prefixedOps = ["add", "sub", "mul", "div", "rem", "cmp"]
            if binaryOpInstruction in prefixedOps:
                prefix = llk.FOP_PREF

        if operandLLVMType == llk.I32:
            prefixedOps = ["div", "rem"]
            if binaryOpInstruction in prefixedOps:
                prefix = llk.SOP_PREF

            prefixedOps = ["cmp"]
            if binaryOpInstruction in prefixedOps:
                prefix = llk.IOP_PREF

        return prefix

    def _CToLLVMType(self, cType: CType) -> str:
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

        if isinstance(returnExpression, IdentifierNode):
            output_string += '\t' + f"%{self.globalRegisterCounter} = {llk.LOAD} {returnType}, {returnType}* %"
            output_string += f"{returnExpression.identifier}, {llk.ALIGN} 4" + '\n'
            output_string += '\t' + f"{llk.RETURN} {returnType} %{self.globalRegisterCounter}" + '\n'
        else:
            output_string = '\t' + f"{llk.RETURN} {returnType} {returnNode.children[0].getValue()}" + '\n'

        # a = 5
        # output_string = '\t' + "ret " + var_value + " " + str(node.children[2].children[-1].children[0].value) + '\n'
        return output_string

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
        retType = self.returnTypeString(identifierNode)     # the LLVM type of the return type

        output_string += f"{llk.DEFINE} {retType} @{identifierNode.identifier}("

        allocations = []

        # Add parameter declarations
        paramIdentifiers = node.getParamIdentifierNodes()
        for pId in paramIdentifiers:
            paramType = self.returnTypeString(pId)
            output_string += f"{paramType} %{pId.identifier}"

            idName = pId.identifier
            allocations.append('\t' + f"%{idName}.addr = {llk.ALLOCA} {paramType}" + '\n')
            allocations.append(self._createStoreStatement(
                paramType, self._getNamedRegisterPrefix(idName) + idName,
                paramType + '*', self._getNamedRegisterPrefix(idName) + idName + ".addr",
                wrap=True))

            # Check object identity, not equality (mem address vs __eq__ method)
            if pId is not paramIdentifiers[-1]:
                output_string += ", "

        # Add parameter allocations and assignments
        # TODO  is this necessary??? What does it do???
        output_string += ") {" + '\n' + "entry:" + '\n'
        output_string += "".join(allocations)


        self.instructions.append(output_string)

        # Visit compound statement
        node.getChild(2).accept(self)

        # Append function closing bracket
        self.instructions.append('}' + '\n' + '\n')

        # update scope
        self._closeScope()

    # TODO
    # TODO
    # TODO
    # TODO
    # TODO
    def visitVar_decl(self, node: Var_declNode):
        self.visitChildren(node)
        return

        identifier = node.getIdentifierNode().identifier
        regType = '@' if self.currentSymbolTable.isGlobal(identifier) else '%'
        dstLocation = self._reserveUnnamedRegister(regType)

        self.currentSymbolTable[identifier].register = dstLocation


        #output_string = self._createStoreStatement(rhsLLVMType, rhsLocation, lhsLLVMType, lhsLocation, wrap=True)

    # TODO  for global variables,
    # TODO      int a;
    # TODO      a = 2;
    # TODO  is not actually valid C code??? definition on same line?
    def visitVar_assig(self, node: Var_assigNode):

        if True:
            lhs = node.getChild(0)
            rhs = node.getChild(1)

            # Visit rhs expression
            node.getChild(1).accept(self)

            rhsLLVMType = self._CToLLVMType(rhs.inferType(self.typeList))
            rhsLocation = self._getExpressionLocation(rhs)

            if not isinstance(lhs, IdentifierNode):
                raise UnsupportedFeature("The left hand side of an assignment MUST be an identifier for now")

            # Visit lhs expression
            node.getChild(0).accept(self)

            lhsLLVMType = self._CToLLVMType(lhs.inferType(self.typeList)) + "*"
            lhsLocation = f"{self._getNamedRegisterPrefix(lhs.identifier)}{lhs.identifier}.addr"

            # TODO if you can assign to not just identifiers, this final assignment should also be diversified
            output_string = self._createStoreStatement(rhsLLVMType, rhsLocation, lhsLLVMType, lhsLocation, wrap=True)
            self.instructions.append(output_string)

    def visitBinaryop(self, node: BinaryopNode):

        lhs: ExpressionNode = node.getChild(0)
        rhs: ExpressionNode = node.getChild(1)
        lhsLLVMType = self._CToLLVMType(lhs.inferType(self.typeList))
        rhsLLVMType = self._CToLLVMType(rhs.inferType(self.typeList))

        lhs.accept(self)    # evaluate lhs
        lhsLocation = self._getExpressionLocation(lhs)

        rhs.accept(self)    # evaluate rhs
        rhsLocation = self._getExpressionLocation(rhs)

        # Reserve register only after operands have reserved theirs
        dstTempRegister: str = self._reserveUnnamedRegister('%')

        binaryOpInstruction = node.getLLVMOpKeyword()
        binaryOpInstruction = self._getBinaryOpPrefix(binaryOpInstruction, lhsLLVMType) + binaryOpInstruction

        output_string = '\t' +\
                        f"{dstTempRegister} = {binaryOpInstruction} {lhsLLVMType} {lhsLocation}, {rhsLLVMType} {rhsLocation}" +\
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
            param.accept(self)

            # Add expression result to call
            output_string += f"{self._CToLLVMType(param.inferType(self.typeList))} {self._getExpressionLocation(param)}"

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

    def visitBlock(self, node: BlockNode):
        self._openScope(node)

        # The self.visitChildren(node) call may be replaced by LLVM generation code
        self.visitChildren(node)

        self._closeScope()

    def visitCompoundstatement(self, node: CompoundstatementNode):
        self._openScope(node)

        # The self.visitChildren(node) call may be replaced by LLVM generation code
        self.visitChildren(node)

        self._closeScope()

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self._openScope(node)

        # The self.visitChildren(node) call may be replaced by LLVM generation code
        self.visitChildren(node)

        self._closeScope()

    def visitIterationstatement(self, node: IterationstatementNode):
        self._openScope(node)

        output_string = ""
        ifn = node
        ifn.getChild(0).accept(self)
        result = self._getExpressionLocation(ifn.getChild(0))
        output_string += '\t' + "br label %while.cond" + '\n'
        output_string += '\n' + "while.cond:" + '\n'
        output_string += '\t' + f"br i1 {result}, label %while.body{self.labelCounter}, label %while.end{self.labelCounter}"
        output_string += '\n' + '\n'
        output_string += f"while.body{self.labelCounter}:" + '\n'
        self.instructions.append(output_string)
        for i in range(2, len(node.children)):
            node.children[i].accept(self)
        self.instructions.append('\n' + "while.end:" + '\n')
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
