from __future__ import annotations

from src.Nodes.ASTreeNode import *
from src.Enumerations import MIPSKeywords as mk, MIPSLocation
from src.Nodes.LiteralNodes import IntegerNode, CharNode
from src.Visitor.GenerationVisitor import GenerationVisitor



class MIPSVisitor(GenerationVisitor):
    def __init__(self, typeList: TypeList):
        self._sectionData = []
        self._sectionText = []

        self._registerDescriptors: dict = dict()    # variable names whose current value is in a register {reg: [IDs]}
        self._addressDescriptors: dict = dict()     # all locations where the current value of a variable is stored # TODO this is register member of SymbolTable???
        self._frameSize: int = 0

        self._argRegisters = mk.getArgRegisters()
        self._varRegisters = mk.getVarRegisters()
        self._tempRegisters = mk.getTempRegisters()
        self._savedRegisters = mk.getSavedRegisters()

        self._reservedLocations = []
        self._SUbase = 0
        super().__init__(typeList)

    # TODO  when loading immediates, there are two options: .data section label + lw OR use li for smaller
    #   immediates (< 2^26) and lui + ori for larger immediates (>= 2^26) (take signedness into account!!)

    @property
    def instructions(self):
        ws = "" * 4
        allInstructions = ".data\n"
        for instruction in self._sectionData:
            allInstructions += ws + instruction + "\n"
        allInstructions += ".text\n"
        for instruction in self._sectionText:
            allInstructions += ws + instruction + "\n"
        return allInstructions

    ######################
    #   HELPER METHODS   #
    ######################
    #

    def _resetFrameSize(self):
        # $fp + $ra
        self._frameSize = mk.REGISTER_SIZE + mk.REGISTER_SIZE

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

    def _constructStackFrame(self, functionCall: FunctioncallNode):
        pass    # TODO review spilling conventions for function calls in lecture 7 slides 31-32

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
            return MIPSLocation()

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

        # TODO reserved actual registers
        reserved = [MIPSLocation(f"$t{num}") for num in range(count)]
        # TODO reserved actual registers

        return reserved

    @staticmethod
    def _load(instrType: str, dstReg: MIPSLocation, src):
        if not (instrType == "I" or instrType == "RW" or instrType == "RB" or instrType == "RA"):
            raise Exception("incorrect mips load type")

        instruction = mk.I_L if instrType == "I" else\
            (mk.R_LW if instrType == "RW" else (mk.R_LB if instrType == "RB" else mk.R_LA))
        return f"{instruction} {dstReg}, {src}"

    @staticmethod
    def _store(instrType: str, dstReg: MIPSLocation, src):
        if not (instrType == "RW" or instrType == "RB"):
            raise Exception("incorrect mips load type")

        instruction = mk.R_SW if instrType == "RW" else mk.R_SB
        return f"{instruction} {src}, {dstReg}"

    def _addTextInstruction(self, instruction: str):
        self._sectionText.append(' '*4 + instruction)

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

        # Construct stack frame
        self._resetFrameSize()

        # TODO for function 'main' no stack frame needed
        self._addTextInstruction(f"{mk.I_ADD_U} {mk.SP}, {mk.SP}, {-self._frameSize}")
        self._addTextInstruction(self._store("RW", MIPSLocation(f"{self._frameSize - 4}({mk.SP})"), mk.FP))
        self._addTextInstruction(f"{mk.R_MOVE}, {mk.FP}, {mk.SP}")
        # move    $sp,$fp
        # lw      $fp,20($sp)
        # addiu   $sp,$sp,24
        # jr      $31

        # Do function body

        # store return values

        # destruct stack frame

        # return
        # jr $ra

        self.visitChildren(node)

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

        # TODO save results before fCall?

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
            loadLiteral = self._load("I", lhsResult, lhs.getValue())
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

        # Calculate parameters
        paramExpressions = node.getParameterNodes()
        reservationsBackup = self._reservedLocations
        self._reservedLocations = []

        for argIdx, paramExp in enumerate(paramExpressions):
            # TODO reserve registers, reserve registers so that final result stored in $a reg or mem

            paramExp.accept(self)

            # TODO move register resultIndex into $a register or memory


        self._reservedLocations = reservationsBackup

        # Spill convention

        # reclaim spilled registers

        # copy return values (for array $v0 contains ptr to first element and array elements are stored in memory???)

    def visitVariabledeclaration(self, node: VariabledeclarationNode):
        # Pre-allocate each declared variable matching space on the stack
        allocAmount = self._byteSize(node.getIdentifierNode().getType())
        # Word sized addressing must be use word aligned addresses
        if allocAmount == mk.WORD_SIZE:
            self._frameSize += mk.WORD_SIZE - self._frameSize % mk.WORD_SIZE
        self._frameSize += allocAmount
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
            loadInstr = self._load(instrType, dst, src)
            self._addTextInstruction(loadInstr)

            self.currentSymbolTable[node.identifier].register = dst

    def visitLiteral(self, node: LiteralNode):
        self._ensureErshovReady(node)
