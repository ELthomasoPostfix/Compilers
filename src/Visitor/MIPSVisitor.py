from __future__ import annotations

from typing import Set

from src.Nodes.ASTreeNode import *
from src.Enumerations import MIPSKeywords as mk, MIPSLocation, MIPSRegisterInfo
from src.Nodes.LiteralNodes import IntegerNode, CharNode
from src.Visitor.GenerationVisitor import GenerationVisitor


class MIPSFunctionDefinition:
    def __init__(self, label: str):
        self.label: str = label
        self.usedSavedRegisters: Set[MIPSLocation] = set()
        self.storeRA: bool = False
        self.instructions = []
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
                    len(self.usedSavedRegisters) + \
                    self._argSlotCount * mk.WORD_SIZE
        # Align frame size on double word size
        twoWords = mk.WORD_SIZE * 2
        return frameSize + (twoWords - frameSize % twoWords)

    def toMips(self):
        ws = " " * 4
        result = [self.label + ":"]
        spillBaseRegister = mk.SP

        # arg slot offset + used saved register offset
        spilledOffset = (self._argSlotCount - 1) * mk.WORD_SIZE + len(self.usedSavedRegisters) * mk.WORD_SIZE
        raLocation: MIPSLocation | None = None

        def addComment(tabCount: int, text: str):
            result[-1] += "\t" * tabCount + MIPSComment(text)

        # Construct stack frame
        result.append(ws + MIPSComment("start of prologue"))
        result.append(ws + f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {-4}")
        addComment(2, "allocate frame pointer")

        result.append(ws + store("RW", mk.FP, MIPSLocation(f"0({mk.SP})")))
        addComment(3, "save frame pointer")

        result.append(ws + f"{move(mk.SP, mk.FP)}")
        addComment(3, "$fp = $sp")

        result.append("")
        result.append(ws + f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {-(self.frameSize - 4)}")
        addComment(2, "allocate rest of stack frame")
        if not self.isLeafFunction():
            raLocation = MIPSLocation(f"{spilledOffset + mk.WORD_SIZE}({mk.SP})")
            result.append(ws + store("RW", mk.RA, raLocation))
            addComment(2, "save return address")

        result.append("")

        # Spill needed saved registers
        for idx, sr in enumerate(self.usedSavedRegisters):
            result.append(ws + store("RW", sr, constructAddress(spilledOffset - idx * mk.WORD_SIZE, spillBaseRegister)))

        result.append(ws + MIPSComment("end of prologue"))
        result.append("")
        result.append(ws + MIPSComment("start of body"))

        result.extend(self.instructions)

        result.append(ws + MIPSComment("end of body"))
        result.append("")
        result.append(ws + MIPSComment("start of epilogue"))

        # Load pre-spilled saved registers
        for idx, sr in enumerate(self.usedSavedRegisters):
            result.append(ws + load("RW", constructAddress(spilledOffset - idx * mk.WORD_SIZE, spillBaseRegister), sr))

        # TODO DO NOT RELOAD ARGUMENT REGISTERS? THEY ARE NOT NEEDED POST FCALL

        result.append("")

        # Destruct stack frame
        if not self.isLeafFunction():
            result.append(ws + load("RW", raLocation, mk.RA))
            addComment(2, "load return address")
        result.append(ws + load("RW", constructAddress(0, mk.FP), mk.FP))
        addComment(2, "load previous frame pointer")
        result.append("")
        result.append(ws + f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {self.frameSize}")
        addComment(2, "deallocate entire stack frame")

        result.append(ws + MIPSComment("end of epilogue"))
        result.append("")

        # return
        result.append(ws + f"{mk.JR} {mk.RA}")

        return result

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
        assert self.storeRA, "Function call should imply storing the return address"

    def isLeafFunction(self):
        return not self.storeRA

    def _usedSavedRegisterCount(self) -> int:
        return len(self.usedSavedRegisters)


class MIPSVisitor(GenerationVisitor):
    def __init__(self, typeList: TypeList):
        self._sectionData = []
        self._sectionText = []
        self._functionDefinitions: List[MIPSFunctionDefinition] = []
        self._currFuncDef: MIPSFunctionDefinition | None = None
        self.addInstrs = True

        self._registerDescriptors: dict = dict()  # variable names whose current value is in a register {reg: [IDs]}
        self._addressDescriptors: dict = dict()  # all locations where the current value of a variable is stored # TODO this is register member of SymbolTable???
        self._frameSize: int = 0

        self._argRegisters = mk.getArgRegisters()
        self._varRegisters = mk.getVarRegisters()
        self._tempRegisters = mk.getTempRegisters()
        self._savedRegisters = mk.getSavedRegisters()

        self._usedSavedRegisters = []
        self._resetSavedUsage()
        self._reservedLocations = []
        self._SUbase = 0
        super().__init__(typeList)

    # TODO  when loading immediates, there are two options: .data section label + lw OR use li for smaller
    #   immediates (< 2^26) and lui + ori for larger immediates (>= 2^26) (take signedness into account!!)

    @property
    def instructions(self):
        allInstructions = ".data\n"
        for instruction in self._sectionData:
            allInstructions += instruction + "\n"
        allInstructions += ".text\n"
        # TODO !!!
        for instruction in self._currFuncDef.toMips():
            allInstructions += instruction + "\n"
        return allInstructions
        # TODO !!!
        for instruction in self._sectionText:
            allInstructions += instruction + "\n"
        return allInstructions

    ######################
    #   HELPER METHODS   #
    ######################
    #

    def _resetFrameSize(self):
        # $fp + $ra
        self._frameSize = mk.REGISTER_SIZE + mk.REGISTER_SIZE

    def _spillRegister(self, register: str):
        pass  # TODO spill the 32-bit (== word) register into memory

    def _stackPush(self, arg: str) -> None:
        """
        Push an argument onto the stack. This method is used in
        constructing a stack frame.

        :param arg: The register to push onto the stack.
        """
        pass  # TODO lengthen the stack frame by the passed argument

    def _stackPop(self):
        pass  # TODO reset stack pointer to frame pointer

    def _constructStackFrame(self, functionCall: FunctioncallNode):
        pass  # TODO review spilling conventions for function calls in lecture 7 slides 31-32

    def _reserveRegister(self, regType: str) -> MIPSLocation:
        """
        Reserve a single register of the specified type.

        :param regType: Type of desired register
        :return: register
        """

        regList = []
        if regType == "s":
            regList = self._savedRegisters
        elif regList == "t":
            regList = self._tempRegisters
        elif regList == "v":
            regList = self._varRegisters
        elif regList == "a":
            regList = self._argRegisters

        if len(regList) == 0:
            # TODO spill some register and return the newly freed register
            #   ==> depends on regType value
            return MIPSLocation("")

        return regList.pop()

    @staticmethod
    def _ensureErshovReady(node: ExpressionNode):
        if not node.ershovNumberIsEvaluated():
            node.evaluateErshovNumber()

    def _ensureRegisterReservations(self, node: ExpressionNode):
        # TODO And function call parameters? The FunctioncallNode is a ExpressionNode!!
        if self._isExpressionRoot(node):
            self._SURootErshov = node.ershovNumber
            self._reservedLocations = self._reserveRegisters(node.ershovNumber)

    @staticmethod
    def _isExpressionRoot(node: ExpressionNode):
        return not isinstance(node.parent, ExpressionNode)

    def _reserveRegisters(self, count: int) -> List[MIPSLocation]:
        """
        Reserve :count: temporary and saved registers. There is a preference for
        temporary registers. A lacking number of temporaries is filled out with
        saved registers.

        :param count: The amount of registers to reserve
        :return: The reserved registers
        """

        reserved = []

        # TODO reserve actual registers
        reserved = [MIPSLocation(f"$s{num}") for num in range(count)]
        # TODO !!!
        self._currFuncDef.usedSavedRegisters.update(reserved)
        # TODO reserve actual registers

        return reserved

    def _addTextLabel(self, labelName: str):
        self._sectionText.append(f"{labelName}:")

    def _addTextInstruction(self, instruction: str, insertIndex: int = -1):
        instruction = ' ' * 4 + instruction
        if insertIndex >= 0:
            self._sectionText.insert(insertIndex, instruction)
            # TODO !!!
            if self.addInstrs:
                self._currFuncDef.instructions.insert(insertIndex, instruction)
            self._sectionText.insert(insertIndex, instruction)
        else:
            # TODO !!!
            if self.addInstrs:
                self._currFuncDef.instructions.append(instruction)
            self._sectionText.append(instruction)

    def _resetSavedUsage(self):
        self._usedSavedRegisters = [0] * len(self._savedRegisters)

    def _addTextWhiteSpace(self, instructionIndex: int):
        self._sectionText[instructionIndex] += "\n"

    def _byteSize(self, cType: CType):
        if cType == self.typeList[BuiltinNames.CHAR]:
            return 1
        elif cType == self.typeList[BuiltinNames.INT] or cType == self.typeList[BuiltinNames.FLOAT]:
            return mk.WORD_SIZE

    ###########################
    #   OTHER VISIT METHODS   #
    ###########################
    #

    def visitFunctiondefinition(self, node: FunctiondefinitionNode):
        # update scope
        self._openScope(node)

        # TODO !!! 0
        self._functionDefinitions.append(MIPSFunctionDefinition(node.getIdentifierNode().identifier))
        self._currFuncDef = self._functionDefinitions[-1]

        # Function body setup
        self._resetSavedUsage()
        self._addTextLabel(node.getIdentifierNode().identifier)
        self._resetFrameSize()
        # TODO for function 'main' no stack frame needed?

        # Do function body
        sfInsertIndex = len(self._sectionText)  # The index to later insert the stack frame construction
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
    # registers.
    #
    # NOTE: results of subexpressions evaluated right before function calls
    #   MUST be stored in a saved register or on the stack, a temporary reg is not safe.

    def visitBinaryop(self, node: BinaryopNode):
        # TODO  Use Sethi-Ullman algorithm adjusted for spilling to use least number of registers in expression evaluation
        #   ==> Sethi-Ullman is an algorithm for binary expression tress (and unary mixed in as well), so putting it
        #   only in visitBinaryop and not visitAssignment or smth ensures that every possible binary expression is
        #   evaluated using it??? What about array operations/access???

        self._ensureErshovReady(node)

        # TODO are reserved registers actually needed? Simply store intermediate results in memory if ever needed
        self._ensureRegisterReservations(node)

        lhs = node.getChild(0)
        rhs = node.getChild(1)
        dstIndex = self._SUbase + node.ershovNumber - 1

        # TODO save results before fCall? ==> Backtrack through tree and use ershov
        #   index (b + k - 1), + take big/small child into consideration, to
        #   know which registers to save
        #   1) preallocate save registers by doing a preliminary pass to locate function calls and to store temp registers
        #   2) move temps to saveds when needed
        #   3) move temps to mem when needed ==> !!! increment frame size !!!²

        if lhs.ershovNumber == rhs.ershovNumber:
            rhs.accept(self)

            self._SUbase -= 1  # Lower base recursively for lhs
            lhs.accept(self)  # TODO save results before fCall?
            self._SUbase += 1  # Reset base recursively after lhs

            # Gather results
            rhsResult = self._reservedLocations[dstIndex]
            lhsResult = self._reservedLocations[dstIndex - 1]

        elif lhs.ershovNumber > rhs.ershovNumber:
            lhs.accept(self)
            rhs.accept(self)

            # Gather results
            rhsResult = self._reservedLocations[self._SUbase + rhs.ershovNumber - 1]
            lhsResult = self._reservedLocations[dstIndex]
        else:
            rhs.accept(self)
            lhs.accept(self)

            # Gather results
            rhsResult = self._reservedLocations[dstIndex]
            lhsResult = self._reservedLocations[self._SUbase + lhs.ershovNumber - 1]

        mipsKeyword = ""

        if isinstance(lhs, LiteralNode):
            mipsKeyword = node.getMIPSROpKeyword('RN')
            loadLiteral = load("I", lhs.getValue(), lhsResult)
            self._addTextInstruction(loadLiteral)
            # TODO take float into account. And ptrs ??? --> part of unary expr??
        elif isinstance(rhs, LiteralNode):
            mipsKeyword = node.getMIPSROpKeyword('I')
            rhsResult = rhs.getValue()
            # TODO take float into account. And ptrs ??? --> part of unary expr??
        else:
            mipsKeyword = node.getMIPSROpKeyword('RN')

        bopInstruction = f"{mipsKeyword} {self._reservedLocations[dstIndex]}, {lhsResult}, {rhsResult}"
        self._addTextInstruction(bopInstruction)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        self._ensureErshovReady(node)
        node.getSubExpression().accept(self)

    def visitUnaryop(self, node: UnaryopNode):
        self._ensureErshovReady(node)
        # single child, Ershov number remains unchanged

        # +, -, !

        self.visitChildren(node)

    # TODO See lecture 7 slides 31-32 for mips spilling conventions
    # TODO See lecture 7 slides 33-34 for stack frame
    def visitFunctioncall(self, node: FunctioncallNode):

        self._ensureErshovReady(node)

        # TODO !!!
        self._currFuncDef.storeRA = True
        self._currFuncDef.adjustArgumentSlotCount(node)

        # Calculate parameters
        paramExpressions = node.getParameterNodes()
        reservationsBackup = self._reservedLocations
        self._reservedLocations = []

        for argIdx, paramExp in enumerate(paramExpressions):
            # TODO reserve registers, reserve registers so that final result stored in $a reg or mem

            paramExp.accept(self)

            # TODO store f"$a{argIdx}" into f"{argIdx*mk.WORD_SIZE}($sp)", because stack pointer should be at the end of
            #  the stack frame, which is where the arg slots are located
            # TODO move register resultIndex into $a register or memory

        self._reservedLocations = reservationsBackup

        # Spill convention

        # reclaim spilled registers

        # copy return values (for array $v0 contains ptr to first element and array elements are stored in memory???)

    def visitVariabledeclaration(self, node: VariabledeclarationNode):
        # Pre-allocate each declared variable matching space on the stack
        allocAmount = self._byteSize(node.getIdentifierNode().getType())
        # Word sized addressing must use word aligned addresses
        if allocAmount == mk.WORD_SIZE:
            self._frameSize += mk.WORD_SIZE - self._frameSize % mk.WORD_SIZE
            # TODO !!!
            self._currFuncDef.framePointerOffset += mk.WORD_SIZE - self._frameSize % mk.WORD_SIZE
        self._frameSize += allocAmount
        # TODO !!!
        self._currFuncDef.framePointerOffset += allocAmount
        self.currentSymbolTable[node.getIdentifierNode().identifier].fpOffset = self._frameSize

    def visitIdentifier(self, node: IdentifierNode):
        self._ensureErshovReady(node)

        if isinstance(node.parent, ExpressionNode):
            instrType = "R" + ("B" if node.inferType(self.typeList) == CharNode.inferType(self.typeList) else "W")
            dst = self._reservedLocations[self._SUbase + node.parent.ershovNumber - 1]
            src = self.currentSymbolTable[node.identifier].register
            if src == "":
                pass
            src = src if src != "" else dst
            loadInstr = load(instrType, src, dst)
            self._addTextInstruction(loadInstr)

            self.currentSymbolTable[node.identifier].register = dst

    def visitLiteral(self, node: LiteralNode):
        self._ensureErshovReady(node)

    def evaluateExpression(self, node: ExpressionNode):
        node.accept(self)
        return MIPSLocation("$t0")

    def visitSelectionstatement(self, node: SelectionstatementNode):
        self._openScope(node)
        self.evaluateExpression(node.getChild(0))

        self._closeScope()


def load(instrType: str, srcAddress: MIPSLocation, dstReg: MIPSLocation):
    if not (instrType == "I" or instrType == "RW" or instrType == "RB" or instrType == "RA"):
        raise Exception("Incorrect mips load type")

    # TODO
    # TODO
    # TODO """"$s" not in srcAddress""" is a quick fix, remove this
    # TODO
    # TODO
    if instrType != "I" and not srcAddress.isAddress() and "$s" not in srcAddress:
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


def store(instrType: str, src, dstReg: MIPSLocation):
    if not (instrType == "RW" or instrType == "RB"):
        raise Exception("incorrect mips load type")

    instruction = mk.R_SW if instrType == "RW" else mk.R_SB
    return f"{instruction} {src}, {dstReg}"


def MIPSComment(text: str):
    return mk.COMMENT_PREFIX + " " + text
