from __future__ import annotations

from typing import Set, Dict, Tuple

from src.Exceptions.exceptions import UnsupportedFeature
from src.Nodes.ASTreeNode import *
from src.Enumerations import MIPSKeywords as mk, MIPSLocation, MIPSRegisterInfo
from src.Nodes.IterationNodes import WhileNode
from src.Nodes.JumpNodes import ContinueNode, BreakNode, ReturnNode
from src.Nodes.LiteralNodes import IntegerNode, CharNode
from src.Nodes.OperatorNodes import NotNode, NegativeNode
from src.Nodes.SelectionNodes import IfNode, ElseNode
from src.SymbolTable import ReadWriteAccess
from src.Visitor.GenerationVisitor import GenerationVisitor


class MIPSFunctionDefinition:
    def __init__(self, label: str):
        self.label: str = label
        self.usedSavedRegisters: Set[MIPSLocation] = set()
        self.isLeaf: bool = True
        self.instructions: List[str] = []
        self.comments: List[List[str]] = []
        self.framePointerOffset: int = 0
        # local data                # Enough stack allocated memory to store all declared variables?
        # return address $ra        # save the previous frame pointer
        # return address $ra        # optional, save the return address in case of function calls
        # n saved register slots    # used to save the contents of saved registers
        # 4 + n Argument slots      # allocated by caller, used by callee to store function arguments
        #                           # in case of callee making a function call. n = max(#func_args - 4, 0) over all
        #                           # function calls done by the caller
        self._argSlotCount: int = 4
        self._savedArgsUpTo: int = 0

    @property
    def frameSize(self):
        # data + $ra + k spilled saved registers + n argument slots
        frameSize = mk.WORD_SIZE + \
                    self.framePointerOffset + \
                    (0 if self.isLeafFunction() else mk.WORD_SIZE) + \
                    len(self.usedSavedRegisters) * mk.WORD_SIZE + \
                    self._argSlotCount * mk.WORD_SIZE
        # Align frame size on double word size
        return alignOnBorder(frameSize, mk.WORD_SIZE * 2)

    def toMips(self):
        result = [self.label + ":"]
        spillBaseRegister = mk.SP

        # arg slot offset + used saved register offset
        spilledOffset = (self._argSlotCount - 1) * mk.WORD_SIZE + len(self.usedSavedRegisters) * mk.WORD_SIZE
        raLocation: MIPSLocation | None = None

        def addComment(tabCount: int, text: str):
            result[-1] += "\t" * tabCount + MIPSComment(text)

        # Construct stack frame
        result.append(mk.WS + MIPSComment("start of prologue"))
        result.append(mk.WS + f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {-4}")
        addComment(2, "allocate frame pointer")

        result.append(mk.WS + store("RW", mk.FP, MIPSLocation(f"0({mk.SP})")))
        addComment(3, "save frame pointer")

        result.append(mk.WS + f"{move(mk.SP, mk.FP)}")
        addComment(3, "$fp = $sp")

        result.append("")
        result.append(mk.WS + f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {-(self.frameSize - 4)}")
        addComment(2, f"allocate rest of stack frame (aligned on double word size = {2 * mk.WORD_SIZE}B)")
        if not self.isLeafFunction():
            raLocation = MIPSLocation(f"{spilledOffset + mk.WORD_SIZE}({mk.SP})")
            result.append(mk.WS + store("RW", mk.RA, raLocation))
            addComment(2, "save return address")

        result.append("")

        # Spill needed saved registers
        for idx, sr in enumerate(self.usedSavedRegisters):
            result.append(
                mk.WS + store("RW", sr, constructAddress(spilledOffset - idx * mk.WORD_SIZE, spillBaseRegister)))

        result.append(mk.WS + MIPSComment("end of prologue"))
        result.append("")
        result.append(mk.WS + MIPSComment("start of body"))

        # Append comments
        fs = "{0:35}{1}"  # formatting string to align comments at column 35
        for cidx, instruction in enumerate(self.instructions):
            result.append(fs.format(instruction, self.getInstructionComment(cidx)))

        result.append(mk.WS + MIPSComment("end of body"))
        result.append("")
        result.append(self.getExitLabel())
        result.append(mk.WS + MIPSComment("start of epilogue"))

        # Load pre-spilled saved registers
        for idx, sr in enumerate(self.usedSavedRegisters):
            result.append(
                mk.WS + load("RW", constructAddress(spilledOffset - idx * mk.WORD_SIZE, spillBaseRegister), sr))

        # TODO DO NOT RELOAD ARGUMENT REGISTERS? THEY ARE NOT NEEDED POST FCALL

        result.append("")

        # Destruct stack frame
        if not self.isLeafFunction():
            result.append(mk.WS + load("RW", raLocation, mk.RA))
            addComment(2, "load return address")
        result.append(mk.WS + load("RW", constructAddress(0, mk.FP), mk.FP))
        addComment(2, "load previous frame pointer")
        result.append("")
        result.append(mk.WS + f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {self.frameSize}")
        addComment(2, "deallocate entire stack frame")

        result.append(mk.WS + MIPSComment("end of epilogue"))
        result.append("")

        # return
        result.append(mk.WS + f"{mk.JR} {mk.RA}")

        return result

    def getExitLabel(self):
        return f"{self.label}.end:"

    def argumentSlotLocation(self, argSlotIdx: int) -> MIPSLocation:
        """
        Get the address for the specified argument slot. Throws assertion error if the
        specified argument slot does not exist.

        :param argSlotIdx: The slot to get the address for
        :return: The address of slot :argSlotIdx:
        """

        assert argSlotIdx < self._argSlotCount
        return MIPSLocation(f"{mk.WORD_SIZE * argSlotIdx}({mk.SP})")

    def adjustArgumentSlotCount(self, node: FunctioncallNode) -> None:
        """
        The number of argument slots is directly based off of the highest number
        of parameters a function call within the current function definition requires.

        :param node: The call to reevaluate the arg slot count based off of
        """

        self._argSlotCount = max(len(node.getParameterNodes()), self._argSlotCount)
        assert self._argSlotCount >= 4, "Incorrectly adjusted argument slot count of function definition"
        assert not self.isLeafFunction(), "Function call should imply storing the return address"

    def isLeafFunction(self):
        return self.isLeaf

    def addInstructionComment(self, comment: str, idx: int = -1):
        assert len(self.instructions) > 0, "Cannot add a comment, no instructions present"
        assert len(self.instructions) > idx, f"Cannot add comment to instruction {idx}, only {len(self.instructions)}" \
                                             f"instructions present"
        self.comments[idx].append(comment)

    def getInstructionComment(self, idx: int):
        commentString = ""
        comments = self.comments[idx]
        for cidx, comment in enumerate(comments):
            commentString += comment
            if cidx < len(comments) - 1:
                commentString += ", "
        return MIPSComment(commentString) if commentString != "" else ""

    def _usedSavedRegisterCount(self) -> int:
        return len(self.usedSavedRegisters)


class MIPSVisitor(GenerationVisitor):
    def __init__(self, typeList: TypeList):
        self._sectionData = []
        self._functionDefinitions: List[MIPSFunctionDefinition] = []
        self._currFuncDef: MIPSFunctionDefinition | None = None

        self._argRegisters = mk.getArgRegisters()
        self._varRegisters = mk.getVarRegisters()
        self._tempRegisters = mk.getTempRegisters()
        self._savedRegisters = mk.getSavedRegisters()

        self._stringCounter = 0

        # variable names whose current value is in a register {reg: [IDs]}
        self._registerDescriptors: Dict[MIPSLocation: List[str]] = dict()
        # all locations where the current value of a variable is stored
        self._addressDescriptors: Dict[str: List[MIPSLocation]] = dict()

        self._reservedLocations = []
        self._expressionEvalDstReg: MIPSLocation | None = None
        self._SUbase = 0
        self.labelCounter = 0
        super().__init__(typeList)

    @property
    def instructions(self):
        allInstructions = ".data\n"
        for instruction in self._sectionData:
            allInstructions += instruction + "\n"
        allInstructions += ".text\n"
        for instruction in self._currFuncDef.toMips():
            allInstructions += instruction + "\n"
        return allInstructions

    ######################
    #   HELPER METHODS   #
    ######################
    #

    def _addAddressDescriptor(self, identifier: str, descriptor: MIPSLocation) -> None:
        self._addressDescriptors.setdefault(identifier, []).append(descriptor)

    def _addRegisterDescriptor(self, register: MIPSLocation, descriptor: str) -> None:
        self._registerDescriptors.setdefault(register, []).append(descriptor)

    def _associateAddressAndRegister(self, identifier: str, register: MIPSLocation) -> None:
        self._addAddressDescriptor(identifier, register)
        self._addRegisterDescriptor(register, identifier)

    def _getUsedAddressDescriptor(self, identifier: str) -> MIPSLocation | None:
        """
        Get an address descriptor used by :identifier:. Preferentially chooses a
        register, else tries to provide an address.

        :param identifier: The identifier to get a used descriptor for
        :return: The descriptor if found, else None
        """

        descriptors = self._getAddressDescriptors(identifier)
        for location in descriptors:
            if location.isRegister():
                return location

        return descriptors[0] if len(descriptors) > 0 else None

    def _getAssignableAddressDescriptor(self, identifier: str):
        """
        Get an address descriptor (register) for :identifier: which stores only
        the value of :identifier:, not for other identifiers.

        :param identifier: The identifier for wich to find a single-possessor register
        :return: The register if found, else None
        """

        for location in self._getAddressDescriptors(identifier):
            if location.isRegister():
                regDescriptors = self._getRegisterDescriptors(location)
                assert identifier in regDescriptors, f"identifier {identifier} is supposed to be stored in" \
                                                     f" register {location}, but is not marked as such"
                if len(regDescriptors) == 1:
                    return location
        return None

    def _registerIsOccupied(self, register: MIPSLocation):
        return len(self._getRegisterDescriptors(register)) > 0

    def _getRegisterDescriptors(self, register: MIPSLocation) -> List[str]:
        """
        Returns the list of identifiers that have their value
        stored in :register:.

        :param register: The register to retrieve the storage information from
        :return: Identifiers
        """

        return self._registerDescriptors.setdefault(register, [])

    def _getAddressDescriptors(self, identifier: str) -> List[MIPSLocation]:
        """
        Returns the list of registers and memory locations the value
        of the identifier is stored in.

        :param identifier: The identifier to retrieve the storage information from
        :return: The storage information
        """

        return self._addressDescriptors.setdefault(identifier, [])

    ## Register spilling based off of register allocation discussed in ppt 10, slides 17-18
    def _spillRegister(self, register: MIPSLocation, expressionType: CType = None) -> None | MIPSLocation:
        """
        Disassociate all identifiers that currently make use of the register with the register.
        This means either altering the address and register descriptor lists or actually spilling
        the contents of the register into an identifier's allocated memory on an identifier by
        identifier basis.

        :param register: The register to spill
        :param expressionType: When spilling for expression eval, its type must be provided
        """

        # Consider spilling each identifier making use of this register
        for identifier in self._getRegisterDescriptors(register):
            # Identifier has its value stored only in register, because len(addressDescriptors) == 1
            # AND identifier is associated with :register:
            if len(self._getAddressDescriptors(identifier)) == 1:
                assert len(self._getAddressDescriptors(identifier)) == 1, "Case len == 0 should never occur," \
                                                                          f" because {register} is associated with" \
                                                                          f" {identifier}"
                idRecord = self.currentSymbolTable[identifier]
                if not idRecord.isFpOffsetInitialized():
                    idRecord.fpOffset = self._stackReserve(idRecord.type)

                instrType = "R" + self._instructionSizeType(idRecord.type)
                spillDst = constructAddress(-idRecord.fpOffset, mk.FP)
                spillInstr = store(instrType, register, spillDst)
                self._addAddressDescriptor(identifier, spillDst)  # associate the spill location with the identifier
                self._addTextInstruction(spillInstr, comment=f"spill {identifier}")

            # If len(self._getAddressDescriptors(identifier)) > 1, then
            # identifier has copies in spare locations, simply disassociate the identifier and register
            self._getAddressDescriptors(identifier).remove(register)  # reg. descript. disassoc. happens after loop

        # reset register descriptors
        self._registerDescriptors[register] = []

        if expressionType is not None:
            # TODO  alter _stackReserve to make spilling reservations temporary (get overwritten by var allocs)
            fpOffset = self._stackReserve(expressionType)
            instrType = "R" + self._instructionSizeType(expressionType)
            spillDst = constructAddress(-fpOffset, mk.FP)
            spillInstr = store(instrType, register, spillDst)
            self._addTextInstruction(spillInstr)

            return spillDst

        return None

    def _spillNeededIntermediateValues(self, functionCall: FunctioncallNode) -> List[
        Tuple[MIPSLocation, MIPSLocation, CType]]:
        """
        A function call implies all non-function-call-preserved registers possibly being
        overwritten as a result of the call. This method goes up the current expression
        evaluation branch starting from :functionCall:, spilling all non-preserved registers
        that store intermediate values of the current expression evaluation.

        :param functionCall: The node to start spilling from
        :return: A list of (non-preserved-register, spill location) pairs
        """

        SUBase = self._SUbase  # Base gets changed in loop
        spills: List[Tuple[MIPSLocation, MIPSLocation, CType]] = []
        currNode: ExpressionNode = functionCall
        r = len(self._reservedLocations)
        identifier: str = functionCall.getIdentifierNode().identifier
        while not self._isExpressionRoot(currNode):  # An expression root has no siblings
            # Function calls store their param results directly into arg registers,
            # so do not spill the other params' final results
            if not isinstance(currNode.parent, FunctioncallNode):
                # The other operand of the expression in case of a parent binary operator
                otherOperand = currNode.getSibling(offset=-1, wrapAround=True)

                # Unary node, no spilling
                if otherOperand == currNode:
                    currNode = currNode.parent
                    continue

                # There are only intermediate results to spill if the current node is the little child
                # in a situation where r >= k (there are enough registers --> non-extended Sethi-Ullman)
                # Consider Sethi-Ullman algorithm steps to decide if currNode is the little child
                #   1) Spilling case (r < k), if currNode is rhs then lhs results are pending,
                #       if currNode is lhs then the rhs results are already calculated AND spilled
                #   2) equal children, if current node is rhs (big child) then lhs results are pending,
                #       if currNode is lhs (little child) then rhs has results and must be spilled
                #   3) unequal children, if current node is big child then little child results
                #       are still pending, if current node is little child then big child results
                #       are ready and must be spilled
                currNodeIsLhs: bool = currNode.getSibling(offset=-1, wrapAround=False) is None
                currNodeIsLittle = currNode.parent.ershovNumber <= r and \
                                   ((currNode.ershovNumber == otherOperand.ershovNumber and currNodeIsLhs) or
                                    currNode.ershovNumber < otherOperand.ershovNumber)

                # Spill current node
                if currNodeIsLittle:
                    # If other operand is a rhs, equal child, it has a base of 1 more than the current base
                    baseOffset = 1 if currNode.ershovNumber == otherOperand.ershovNumber and currNodeIsLhs else 0
                    spillType = otherOperand.inferType(self.typeList)
                    spillRegister = self._getReservedLocation(otherOperand, SUBase + baseOffset)
                    spillAddress = self._spillRegister(spillRegister, spillType)
                    spills.append((spillRegister, spillAddress, spillType))

                if currNode.ershovNumber == otherOperand.ershovNumber and not currNodeIsLhs:
                    SUBase -= 1

            currNode = currNode.parent

            # Extended Sethi-Ullman takes care of spilling on its own
            if currNode.ershovNumber > r:
                break

        self._SUbase = SUBase  # restore base
        return spills

    def _instructionSizeType(self, cType: CType):
        return "B" if not cType.isPointerType() and cType == CharNode.inferType(self.typeList) else "W"

    def _functionParamsToStackFrameLocations(self, functionDefinition: FunctiondefinitionNode) -> List[Tuple[str, MIPSLocation]]:
        """
        Convert a list of parameters to a function call to the argument registers and or memory
        locations their values are stored in.

        :param functionDefinition: The function definition whose params to convert
        :return: A list of (param identifier, arg location) pairs
        """

        totalOffset = 0
        locations: List[Tuple[str, MIPSLocation]] = []
        for idx, param in enumerate(functionDefinition.getParamIdentifierNodes()):
            if idx < 4:
                locations.append((param.identifier, self._argRegisters[idx]))
            else:
                allocAmount = self._byteSize(param.getType())
                totalOffset = alignOnBorder(totalOffset + allocAmount, allocAmount)
                argSlotAddress = constructAddress(totalOffset, mk.FP)
                locations.append((param.identifier, argSlotAddress))

        return locations

    def _stackReserve(self, cType: CType) -> int:
        """
        Reserve enough bytes on the stack to store a single variable
        of type :cType:.

        :param cType: The type of the value to store on the stack
        :return: The offset to the frame pointer, so that 'offset($fp)'
            identifies the allocated memory address
        """

        # TODO Keep a FunctionBody.spillOffset so that
        #       alignOnBorder(FB.framePointerOffset + FunctionBody.spillOffset, mk.WORD_SIZE) + allocAmount
        #   is the memory address assigned to a call to _stackReserve in the context of more spilling (also increase spillOffset),
        #   and
        #       alignOnBorder(FB.framePointerOffset, mk.WORD_SIZE) + allocAmount
        #   is the memory address assigned to a call to _stackReserve in the context of reserving memory in all other
        #   cases.

        allocAmount = self._byteSize(cType)
        # Word sized addressing must use word aligned addresses
        if allocAmount == mk.WORD_SIZE:
            self._currFuncDef.framePointerOffset = alignOnBorder(self._currFuncDef.framePointerOffset, mk.WORD_SIZE)
        self._currFuncDef.framePointerOffset += allocAmount

        return self._currFuncDef.framePointerOffset

    def _getReservedLocation(self, expression: ExpressionNode, base: int) -> MIPSLocation:
        SUIndex = expression.sethiUllmanNumber(base)
        return self._reservedLocations[min(SUIndex, len(self._reservedLocations) - 1)]

    def _getReservedExpressionLocation(self, expression: ExpressionNode) -> MIPSLocation:
        return self._expressionEvalDstReg if self._isExpressionRoot(expression) and \
                                             self._expressionEvalDstReg is not None \
            else self._getReservedLocation(expression, self._SUbase)

    def _getAssignableSavedRegister(self) -> MIPSLocation | None:
        """
        Reserve a single saved register. May spill the least-in-use register contents
        to obtain/reserve the requested register.

        :return: A reserved saved register
        """

        result = ""
        minAmount = 1000
        minRegister = -1

        for register in self._savedRegisters:
            if minAmount > len(self._getRegisterDescriptors(register)):
                minAmount = len(self._getRegisterDescriptors(register))
                minRegister = register
            if minAmount == 0:
                result = register
                break

        if result == "":
            result = minRegister
            self._spillRegister(result)

        # TODO move this to visitVar_assig()?
        self._currFuncDef.usedSavedRegisters.add(result)

        return result

    @staticmethod
    def _isExpressionRoot(node: ExpressionNode):
        # Has nor ExpressionNode parent or
        # has a UnaryexpressionNode parent which has no ExpressionNode parent
        return node is not None and (not isinstance(node.parent, ExpressionNode) or
                                     (isinstance(node.parent, UnaryexpressionNode) and
                                      not isinstance(node.parent.parent, ExpressionNode)))

    def _reserveRegisters(self, amount: int) -> List[MIPSLocation]:
        """
        Reserve :count: temporary registers.

        :param amount: The amount of registers to reserve
        :return: The reserved registers
        """

        # Just use temporary registers for expressions, mixing in saved registers
        # may get messy?
        # TODO consider spilling saved registers to use in expressions???
        return self._tempRegisters[:amount]

    def _addTextLabel(self, labelName: str):
        self._currFuncDef.instructions.append(labelName + ":")
        self._currFuncDef.comments.append([""])

    def _addTextInstruction(self, instruction: str, insertIndex: int = -1, comment: str = ""):
        instruction = ' ' * 4 + instruction
        comment = [] if comment == "" else [comment]
        if insertIndex >= 0:
            self._currFuncDef.instructions.insert(insertIndex, instruction)
            self._currFuncDef.comments.insert(insertIndex, comment)
        else:
            self._currFuncDef.instructions.append(instruction)
            self._currFuncDef.comments.append(comment)

    def _byteSize(self, cType: CType):
        if cType.isPointerType():  # TODO take dereference unary ops into account??
            return mk.WORD_SIZE
        elif cType == self.typeList[BuiltinNames.CHAR]:
            return mk.BYTE_SIZE
        elif cType == self.typeList[BuiltinNames.INT] or cType == self.typeList[BuiltinNames.FLOAT]:
            return mk.WORD_SIZE

    def _closeScope(self):
        # Purge all saved register usage information of the current scope
        for identifier in self.currentSymbolTable.mapping.keys():
            for location in self._getAddressDescriptors(identifier):
                if location.isRegister():
                    self._getRegisterDescriptors(location).remove(identifier)

            self._getAddressDescriptors(identifier).clear()
        super()._closeScope()

    ###########################
    #   OTHER VISIT METHODS   #
    ###########################
    #

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        # update scope
        self._openScope(node)

        self._functionDefinitions.append(MIPSFunctionDefinition(node.getIdentifierNode().identifier))
        self._currFuncDef = self._functionDefinitions[-1]

        # TODO this
        # Associate the parameter variables with the arg registers or their memory location
        paramLocations = self._functionParamsToStackFrameLocations(node)

        # Do function body
        self.visitChild(node, 2)  # Generate code for the function body

        # update scope
        self._closeScope()

    ###############################
    #   EXPRESSION EVAL METHODS   #
    ###############################
    #
    # Expression evaluation makes use of the Sethi-Ullman algorithm adjusted
    # for finite registers. The calculation of the Strahler/Ershov number happens
    # dynamically, as does the reservation of registers and stack memory locations.
    # The register index in the algorithm is used as an index for the list of reserved
    # registers. Read the comments in _reserveRegisters() for more information on
    # which registers are reserved for expression evaluation.
    #
    # NOTE: results of subexpressions evaluated right before function calls
    #   MUST be stored in a saved register or on the stack, a temporary reg is not safe.

    def visitBinaryop(self, node: BinaryopNode):
        # TODO  Use Sethi-Ullman algorithm adjusted for spilling to use least number of registers in expression evaluation
        #   ==> Sethi-Ullman is an algorithm for binary expression trees (and unary mixed in as well), so putting it
        #   only in visitBinaryop and not visitAssignment or smth ensures that every possible binary expression is
        #   evaluated using it??? What about array operations/access???

        lhs = node.getChild(0)
        rhs = node.getChild(1)

        # TODO save results before fCall? ==> Backtrack through tree and use ershov
        #   index (b + k - 1), + take big/small child into consideration, to
        #   know which registers to save
        #   1) preallocate save registers by doing a preliminary pass to locate function calls and to store temp registers
        #   2) move temps to saveds when needed
        #   3) move temps to mem when needed ==> !!! increment frame size !!!²

        # The number of available/reserved registers
        r = len(self._reservedLocations)

        # exp. eval. using spilling     (ppt 10 slide 33)
        if node.ershovNumber > r:
            rhsIsBig = rhs.ershovNumber >= lhs.ershovNumber
            # In case of equal children, choose rhs as big child and lhs as little child
            bigChild = rhs if rhsIsBig else lhs
            littleChild = lhs if rhsIsBig else rhs
            bigType = bigChild.inferType(self.typeList)

            # Generate code for big child
            self._SUbase = 0
            bigResult = self.evaluateExpression(bigChild)
            spillAddress = self._spillRegister(bigResult, bigType)
            self._currFuncDef.addInstructionComment(f"r > k ({r > node.ershovNumber}), spill big child in R_{r - 1}")

            # Generate code for little child
            self._SUbase = 0 if littleChild.ershovNumber >= r else r - littleChild.ershovNumber - 1
            littleResult = self.evaluateExpression(littleChild)

            # Recover big child
            bigResult = self._reservedLocations[-2]  # load big child back into R_{r-1}
            loadType = "R" + self._instructionSizeType(bigType)
            loadInstr = load(loadType, spillAddress, bigResult)
            self._addTextInstruction(loadInstr, comment=f"reload big child result into register R_{r - 1}")

            if rhsIsBig:
                rhsResult = bigResult
                lhsResult = littleResult
            else:
                lhsResult = bigResult
                rhsResult = littleResult

        # exp. eval. without spilling, equal children
        elif lhs.ershovNumber == rhs.ershovNumber:
            self._SUbase += 1  # Increment base recursively for rhs
            rhsResult = self.evaluateExpression(rhs)
            self._SUbase -= 1  # Decrement base recursively after rhs
            lhsResult = self.evaluateExpression(lhs)
        # exp. eval. without spilling, left child is big child
        elif lhs.ershovNumber > rhs.ershovNumber:
            lhsResult = self.evaluateExpression(lhs)
            rhsResult = self.evaluateExpression(rhs)
        # exp. eval. without spilling, right child is big child
        else:
            rhsResult = self.evaluateExpression(rhs)
            lhsResult = self.evaluateExpression(lhs)

        mipsKeyword = ""

        # If the lhs is a literal, load it in
        if isinstance(lhs, LiteralNode):
            mipsKeyword = node.getMIPSROpKeyword('RN')
            literalLoadedReg = self._getReservedLocation(lhs, self._SUbase)
            loadLiteral = load("I", lhsResult, literalLoadedReg)
            self._addTextInstruction(loadLiteral, comment=f"literal lhs ({lhsResult} {mipsKeyword} ...)")
            lhsResult = literalLoadedReg
            # TODO take float into account. And ptrs ??? --> part of unary expr??
        elif isinstance(rhs, LiteralNode):
            mipsKeyword = node.getMIPSROpKeyword('I')
            rhsResult = rhs.getValue()
            # TODO take float into account. And ptrs ??? --> part of unary expr??
        else:
            mipsKeyword = node.getMIPSROpKeyword('RN')

        # Use a separately specified destination for the result if possible.
        # Else the Sethi-Ullman specified location is used.
        dstRegister = self._getReservedExpressionLocation(node)
        bopInstruction = f"{mipsKeyword} {dstRegister}, {lhsResult}, {rhsResult}"
        self._addTextInstruction(bopInstruction)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        node.getSubExpression().accept(self)

    def visitUnaryop(self, node: UnaryopNode):
        # single child, Ershov number remains unchanged

        # +, -, !

        if isinstance(node, NotNode) or isinstance(node, NegativeNode):
            unaryInstruction = ""
            comment = ""
            dstRegister = self._getReservedExpressionLocation(node)
            srcRegister = self.evaluateExpression(node.getSubExpression())
            mipsKeyword = node.getMIPSROpKeyword('R')
            if isinstance(node, NotNode):
                unaryInstruction = f"{mipsKeyword} {dstRegister}, {srcRegister}, 1"
                comment = "unary logical not"
            elif isinstance(node, NegativeNode):
                unaryInstruction = f"{mipsKeyword} {dstRegister}, {srcRegister}"
                comment = "unary minus"


            self._addTextInstruction(unaryInstruction)

            if comment != "":
                self._currFuncDef.addInstructionComment(comment)

        # TODO implement Sethi-Ullman with spilling here as well??????????
        # TODO implement Sethi-Ullman with spilling here as well??????????
        # TODO implement Sethi-Ullman with spilling here as well??????????

        self.visitChildren(node)

    def concatinateString(self, input):
        init_string = input[0]
        init_stringc = 0
        output_string = ""
        acc_list = ['i', 'd', 's']
        del input[0]
        i = 0
        while i < len(init_string):
            if init_string[i] == '%':
                if init_string[i + 1] in acc_list:
                    output_string += str(input[init_stringc])
                    init_stringc += 1
                    i += 2
            else:
                output_string += init_string[i]
                i += 1
        return output_string

    # TODO See lecture 7 slides 31-32 for mips spilling conventions
    # TODO See lecture 7 slides 33-34 for stack frame
    def visitFunctioncall(self, node: FunctioncallNode):
        identifier = node.getIdentifierNode()
        if identifier.identifier == "printf":
            temp = []
            for i in range(1, len(node.children)):
                temp.append(node.getChild(i).getValue())
            output_str = self.concatinateString(temp)
            self._sectionData.append(f"string{self._stringCounter}: .asciiz \"{output_str}\"")
            self._addTextInstruction("li $v0, 4")
            self._addTextInstruction(f"la $a0, string{self._stringCounter}")
            self._addTextInstruction("syscall")

        # Setup
        self._currFuncDef.isLeaf = False
        self._currFuncDef.adjustArgumentSlotCount(node)

        # Save intermediate results
        # [(register, spillAddress, spill type), ]
        spilledIntermediaries: List[Tuple[MIPSLocation, MIPSLocation, CType]]
        spilledIntermediaries = self._spillNeededIntermediateValues(node)
        self._currFuncDef.addInstructionComment("spill intermediate results ...", -len(spilledIntermediaries))
        self._currFuncDef.addInstructionComment(f"... before function call: {node.toLegibleRepr(self.typeList)}")

        # Calculate parameters
        paramExpressions = node.getParameterNodes()

        # TODO this \/
        # Save current function definition arguments

        for argIdx, paramExp in enumerate(paramExpressions):
            # TODO reserve registers, reserve registers so that final result stored in $a reg or mem

            # TODO implement Sethi-Ullman with spilling here as well??????????
            # TODO implement Sethi-Ullman with spilling here as well??????????
            # TODO implement Sethi-Ullman with spilling here as well??????????

            paramLoc = self.evaluateExpression(paramExp, )

            # TODO store f"$a{argIdx}" into f"{argIdx*mk.WORD_SIZE}($sp)", because stack pointer should be at the end of
            #  the stack frame, which is where the arg slots are located
            # TODO move register resultIndex into $a register or memory

        # copy return values (for array $v0 contains ptr to first element and array elements are stored in memory???)
        retMovInstr = move(self._varRegisters[0], self._getReservedExpressionLocation(node))
        self._addTextInstruction(retMovInstr, comment=f"load return value of: {node.toLegibleRepr(self.typeList)}")

        # Recover spilled expression intermediary values
        for spillRegister, spillAddress, spillType in spilledIntermediaries:
            instrType = "R" + self._instructionSizeType(spillType)
            self._addTextInstruction(load(instrType, spillAddress, spillRegister))

        self._currFuncDef.addInstructionComment("recover intermediate results ...", -len(spilledIntermediaries))
        self._currFuncDef.addInstructionComment(f"... after function call: {node.toLegibleRepr(self.typeList)}")

    def visitVar_assig(self, node: Var_assigNode):
        rhs: ExpressionNode = node.getChild(1)
        lhs: IdentifierNode = node.getIdentifierNode()

        if not isinstance(lhs, IdentifierNode):
            raise UnsupportedFeature("The lhs of an assignment must be an identifier for now", location=lhs.location)

        # Select an overwritable register of lhs, else None
        lhsLoc = self._getAssignableAddressDescriptor(lhs.identifier)
        # No overwritable register, get saved register (possible spilling)
        if lhsLoc is None:
            lhsLoc = self._getAssignableSavedRegister()
            if isinstance(lhs, IdentifierNode):
                self._associateAddressAndRegister(lhs.identifier, lhsLoc)

        self.evaluateExpression(rhs, resultDstReg=lhsLoc)

        if isinstance(lhs, IdentifierNode) and len(self._currFuncDef.instructions) != 0:
            self._currFuncDef.addInstructionComment(f"assig {lhs.identifier}")

    def evaluateExpression(self, expression: ExpressionNode, resultDstReg: MIPSLocation | None = None):
        """
        Evaluate the passed expression and return the register containing the final result.
        In the case of a literal that is not the root of an expression, the literal value
        is returned instead.

        :param expression: The expression to evaluate
        :param resultDstReg: A specified location the result of the evaluation should be stored at
        :return: The result of the evaluation
        """

        # TODO for function return $v0 ????

        if not expression.ershovNumberIsEvaluated():
            expression.evaluateErshovNumber()

        dstLoc = ""
        if self._isExpressionRoot(expression):
            self._reservedLocations = self._reserveRegisters(expression.ershovNumber)
            assert resultDstReg is None or resultDstReg.isRegister()
            self._expressionEvalDstReg = resultDstReg

        # Expression was a single literal
        if isinstance(expression, LiteralNode):
            value = str(expression.getValue())

            # If Literal not part of an expression, store it in an intermediate register
            if self._isExpressionRoot(expression):
                dstRegister = self._getReservedLocation(expression, self._SUbase) if resultDstReg is None \
                    else resultDstReg
                self._addTextInstruction(load('I', value, dstRegister))
                value = dstRegister

            dstLoc = value
        # Sub-expression is an identifier
        elif isinstance(expression, IdentifierNode):

            # Ensure that an identifier part of an expression gets loaded
            # into a register
            src: MIPSLocation | None = self._getUsedAddressDescriptor(expression.identifier)
            if src is None or src.isAddress():
                # Prepare load instruction for src
                instrType = "R" + self._instructionSizeType(expression.inferType(self.typeList))
                dstRegister = self._getReservedLocation(expression, self._SUbase) \
                    if resultDstReg is None or not self._isExpressionRoot(expression) \
                    else resultDstReg
                comment: str = f"load {expression.identifier}"

                # Using uninitialized variable, allocate stack memory
                if src is None:
                    record = self.currentSymbolTable[expression.identifier]
                    if not record.isFpOffsetInitialized():
                        record.fpOffset = self._stackReserve(expression.getType())
                    src = constructAddress(-record.fpOffset, mk.FP)

                    # Log/associate assigned stack memory
                    self._addAddressDescriptor(expression.identifier, src)
                    comment += " (uninitialized)"

                loadInstr = load(instrType, src, dstRegister)
                self._addTextInstruction(loadInstr, comment=comment)

                # associate assigned register with identifier
                self._associateAddressAndRegister(expression.identifier, dstRegister)
                dstLoc = dstRegister
            else:
                dstLoc = src
        else:
            # Evaluate the expression
            expression.accept(self)

            # Get the result according to Sethi-Ullman
            dstLoc = self._getReservedLocation(expression, self._SUbase)

        # TODO free registers???
        if self._isExpressionRoot(expression):
            pass

        return dstLoc

    def visitIterationstatement(self, node: IterationstatementNode):
        self._openScope(node)
        self.labelCounter = self.labelCounter + 1
        self._addTextInstruction(f"b $while.head{self.labelCounter}\n")
        self._addTextLabel(f"$while.body{self.labelCounter}")
        temp = self.labelCounter
        for i in range(1, len(node.children)):
            node.getChild(i).accept(self)
        self._addTextLabel(f"\n$while.head{temp}")
        result = self.evaluateExpression(node.getChild(0))
        self._addTextInstruction(f"bne {result},$0,$while.body{temp}\n")
        self._addTextLabel(f"$while.exit{temp}")
        self.labelCounter += 1
        self._closeScope()

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self._openScope(node)
        while True:
            elseCheck = False
            baseIdx, endIdx = 0, len(node.children)
            if isinstance(node, IfNode):
                str_comp = self._evaluateExpression(node.getChild(0))
            if isinstance(node, IfNode):
                self._addTextInstruction(f"beq {str_comp},$0,$L{self.labelCounter}\n")
                if isinstance(node.getChild(-1), ElseNode):
                    elseCheck = True
                baseIdx = 1
                endIdx -= 1
            for i in range(baseIdx, endIdx):
                node.children[i].accept(self)
            if not elseCheck:
                self._addTextLabel(f"$L{self.labelCounter}")
                self.labelCounter += 1
                break
            node = node.getChild(-1)
            self.labelCounter += 1
            self._addTextInstruction(f"b $L{self.labelCounter}")
            self._addTextLabel(f"$L{self.labelCounter - 1}")
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

    def visitJumpstatement(self, node: JumpstatementNode):
        brent_postfix = ""
        if isinstance(node, ContinueNode):
            brent_postfix = "head"
        if isinstance(node, BreakNode):
            brent_postfix = "exit"
        if isinstance(node, ReturnNode):
            self.evaluateExpression(node.getChild(0), self._varRegisters[0])
            self._addTextInstruction(f"j {self._currFuncDef.getExitLabel()}")
            return
        self._addTextInstruction(f"j $while.{brent_postfix}{self.labelCounter}")
        self._currFuncDef.addInstructionComment("break")


#########################################
#   MIPS Instruction Creation METHODS   #
#########################################
#


def load(instrType: str, srcAddress, dstReg: MIPSLocation):
    if not (instrType == "I" or instrType == "RW" or instrType == "RB" or instrType == "RA"):
        raise Exception("Incorrect mips load type")

    if instrType != "I" and not srcAddress.isAddress():
        raise Exception(f"Loading from incorrect source (should be address): load from '{srcAddress}'")

    if not dstReg.isRegister():
        raise Exception(f"Loading into incorrect destination (should be register): load into '{dstReg}'")

    instruction = mk.I_L if instrType == "I" else \
        (mk.R_LW if instrType == "RW" else (mk.R_LB if instrType == "RB" else mk.R_LA))
    return f"{instruction} {dstReg}, {srcAddress}"


def move(srcReg: MIPSLocation, dstReg: MIPSLocation):
    return f"{mk.R_MOVE}, {dstReg}, {srcReg}"


def constructAddress(offset: int, register: MIPSLocation) -> MIPSLocation:
    """
    Construct a mips address of the format 'offset(register)'

    :param offset: The offset to the register contents
    :param register: The register contents to use as an address
    :return: The address MIPSLocation
    """

    return MIPSLocation(f"{offset}({register})")


def store(instrType: str, src: MIPSLocation, dstReg: MIPSLocation):
    if not (instrType == "RW" or instrType == "RB"):
        raise Exception("incorrect mips load type")

    assert dstReg.isAddress(), "Must store into an address"

    instruction = mk.R_SW if instrType == "RW" else mk.R_SB
    return f"{instruction} {src}, {dstReg}"


def MIPSComment(text: str):
    return mk.COMMENT_PREFIX + " " + text


def alignOnBorder(value: int, border: int):
    mod = value % border
    if mod == 0:
        return value
    return value + border - mod
