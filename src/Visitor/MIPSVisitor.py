from __future__ import annotations

from typing import Set

from src.Nodes.ASTreeNode import *
from src.Enumerations import MIPSKeywords as mk, MIPSLocation, MIPSRegisterInfo
from src.Nodes.LiteralNodes import IntegerNode, CharNode
from src.Nodes.SelectionNodes import IfNode, ElseNode
from src.Visitor.GenerationVisitor import GenerationVisitor


class MIPSFunctionDefinition:
    def __init__(self, label: str):
        self.label: str = label
        self.usedSavedRegisters: Set[MIPSLocation] = set()
        self.isLeaf: bool = True
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
        result = [self.label + ":"]
        spillBaseRegister = mk.SP

        # arg slot offset + used saved register offset
        spilledOffset = (self._argSlotCount - 1) * mk.WORD_SIZE + len(self.usedSavedRegisters) * mk.WORD_SIZE
        raLocation: MIPSLocation | None = None

        def addComment(tabCount: int, text: str):
            result[-1] += "\t"*tabCount + MIPSComment(text)

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
        addComment(2, "allocate rest of stack frame")
        if not self.isLeafFunction():
            raLocation = MIPSLocation(f"{spilledOffset + mk.WORD_SIZE}({mk.SP})")
            result.append(mk.WS + store("RW", mk.RA, raLocation))
            addComment(2, "save return address")

        result.append("")

        # Spill needed saved registers
        for idx, sr in enumerate(self.usedSavedRegisters):
            result.append(mk.WS + store("RW", sr, constructAddress(spilledOffset - idx * mk.WORD_SIZE, spillBaseRegister)))

        result.append(mk.WS + MIPSComment("end of prologue"))
        result.append("")
        result.append(mk.WS + MIPSComment("start of body"))

        result.extend(self.instructions)

        result.append(mk.WS + MIPSComment("end of body"))
        result.append("")
        result.append(mk.WS + MIPSComment("start of epilogue"))

        # Load pre-spilled saved registers
        for idx, sr in enumerate(self.usedSavedRegisters):
            result.append(mk.WS + load("RW", constructAddress(spilledOffset - idx * mk.WORD_SIZE, spillBaseRegister), sr))

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
        assert self.isLeaf, "Function call should imply storing the return address"

    def isLeafFunction(self):
        return self.isLeaf
    
    def _usedSavedRegisterCount(self) -> int:
        return len(self.usedSavedRegisters)


class MIPSVisitor(GenerationVisitor):
    def __init__(self, typeList: TypeList):
        self._sectionData = []
        self._sectionText = []
        self._functionDefinitions: List[MIPSFunctionDefinition] = []
        self._currFuncDef: MIPSFunctionDefinition | None = None


        self._argRegisters = mk.getArgRegisters()
        self._varRegisters = mk.getVarRegisters()
        self._tempRegisters = mk.getTempRegisters()
        self._savedRegisters = mk.getSavedRegisters()

        # variable names whose current value is in a register {reg: [IDs]}
        self._registerDescriptors: dict = dict()
        # all locations where the current value of a variable is stored
        self._addressDescriptors: dict = dict()

        self._usedSavedRegisters = []
        self._resetSavedUsage()
        self._reservedLocations = []
        self._SUbase = 0
        self.labelCounter = 0
        super().__init__(typeList)

    # TODO  when loading immediates, there are two options: .data section label + lw OR use li for smaller
    #   immediates (< 2^26) and lui + ori for larger immediates (>= 2^26) (take signedness into account!!)

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

    def _spillRegister(self, register: str):
        pass    # TODO spill the 32-bit (== word) register into memory

    def _stackPush(self, arg: str) -> None:
        """
        Push an argument onto the stack. This method is used in
        constructing a stack frame.

        :param arg: The register to push onto the stack.
        """
        pass    # TODO lengthen the stack frame by the passed argument

    def _stackPop(self):
        pass    # TODO reset stack pointer to frame pointer

    def _stackReserve(self, cType: CType) -> int:
        """
        Reserve enough bytes on the stack to store a single variable
        of type :cType:.

        :param cType: The type of the value to store on the stack
        :return: The offset to the frame pointer, so that 'offset($fp)'
            identifies the allocated memory address
        """

        allocAmount = self._byteSize(cType)
        # Word sized addressing must use word aligned addresses
        if allocAmount == mk.WORD_SIZE:
            self._currFuncDef.framePointerOffset += mk.WORD_SIZE - self._currFuncDef.framePointerOffset % mk.WORD_SIZE
        self._currFuncDef.framePointerOffset += allocAmount

        return self._currFuncDef.framePointerOffset

    def _reserveRegister(self, regType: str) -> MIPSLocation | None:
        """
        Reserve a single register of the specified type.

        :param regType: Type of desired register
        :return: register if any available, else None
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
            return None

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
        self._currFuncDef.usedSavedRegisters.update(reserved)
        # TODO reserve actual registers

        return reserved

    def _addTextLabel(self, labelName: str):
        self._currFuncDef.instructions.append(labelName + ":")

    def _addTextInstruction(self, instruction: str, insertIndex: int = -1):
        instruction = ' '*4 + instruction
        if insertIndex >= 0:
            self._currFuncDef.instructions.insert(insertIndex, instruction)
        else:
            self._currFuncDef.instructions.append(instruction)

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

        self._functionDefinitions.append(MIPSFunctionDefinition(node.getIdentifierNode().identifier))
        self._currFuncDef = self._functionDefinitions[-1]

        # Function body setup
        self._resetSavedUsage()
        # TODO for function 'main' no stack frame needed?

        # Do function body
        self.visitChild(node, 2)    # Generate code for the function body

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
        #   ==> Sethi-Ullman is an algorithm for binary expression trees (and unary mixed in as well), so putting it
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

            self._SUbase -= 1       # Lower base recursively for lhs
            lhs.accept(self)        # TODO save results before fCall?
            self._SUbase += 1       # Reset base recursively after lhs

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

        self._currFuncDef.isLeaf = False
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
        return
        # Pre-allocate each declared variable matching space on the stack
        allocatedAddress = self._stackReserve(node.getIdentifierNode().getType())
        self.currentSymbolTable[node.getIdentifierNode().identifier].fpOffset = -allocatedAddress

    def visitIdentifier(self, node: IdentifierNode):
        self._ensureErshovReady(node)

        if isinstance(node.parent, ExpressionNode):
            src: MIPSLocation = self.currentSymbolTable[node.identifier].register
            if not src.isRegister():
                instrType = "R" + ("B" if node.inferType(self.typeList) == CharNode.inferType(self.typeList) else "W")
                dst = self._reservedLocations[self._SUbase + node.parent.ershovNumber - 1]
                comment: str = f"load {node.identifier}"
                if src == "":
                    src = constructAddress(self._stackReserve(node.getType()), mk.FP)
                    self.currentSymbolTable[node.identifier].register = src
                    comment = " (undeclared variable)"
                loadInstr = load(instrType, src, dst, comment)
                self._addTextInstruction(loadInstr)

                self.currentSymbolTable[node.identifier].register = dst

    def visitVar_assig(self, node: Var_assigNode):
        rhs: ExpressionNode = node.getChild(1)
        lhs: IdentifierNode = node.getIdentifierNode()

        rhsLoc = self.evaluateExpression(rhs)
        lhsLoc = self.currentSymbolTable[lhs.identifier].register

        if isinstance(rhs, LiteralNode):
            self._addTextInstruction(load("I", rhs.getValue(), self._reserveRegister("t")))

        if lhsLoc.isRegister():
            # TODO Make the expression load directly into the location of lhs???
            self._addTextInstruction(move(rhsLoc, lhsLoc))
        elif lhsLoc.isAddress():
            # TODO what in case of pointers???
            self.currentSymbolTable[lhs.identifier].register = rhsLoc
        else:
            raise Exception("variable assignment lhs location guard clause")

    def visitLiteral(self, node: LiteralNode):
        self._ensureErshovReady(node)

    def evaluateExpression(self, node: ExpressionNode):
        node.accept(self)
        return MIPSLocation("$t0")

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

#########################################
#   MIPS Instruction Creation METHODS   #
#########################################
#


def load(instrType: str, srcAddress: MIPSLocation, dstReg: MIPSLocation, comment: str = ""):
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

    instruction = mk.I_L if instrType == "I" else\
        (mk.R_LW if instrType == "RW" else (mk.R_LB if instrType == "RB" else mk.R_LA))
    return f"{instruction} {dstReg}, {srcAddress}" + ("" if comment == "" else ('\t'*2 + MIPSComment(comment)))


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


def store(instrType: str, src: MIPSLocation, dstReg: MIPSLocation, comment: str = ""):
    if not (instrType == "RW" or instrType == "RB"):
        raise Exception("incorrect mips load type")

    assert dstReg.isAddress(), "Must store into an address"

    instruction = mk.R_SW if instrType == "RW" else mk.R_SB
    return f"{instruction} {src}, {dstReg}" + ("" if comment == "" else ('\t'*2 + MIPSComment(comment)))


def MIPSComment(text: str):
    return mk.COMMENT_PREFIX + " " + text
