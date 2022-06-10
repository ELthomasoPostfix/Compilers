from __future__ import annotations

from typing import Set, Dict

from src.Exceptions.exceptions import UnsupportedFeature
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
        addComment(2, "allocate rest of stack frame")
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

        result.extend(self.instructions)

        result.append(mk.WS + MIPSComment("end of body"))
        result.append("")
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

    def _addAddressDescriptor(self, identifier: IdentifierNode, descriptor: MIPSLocation):
        self._addressDescriptors.setdefault(identifier.identifier, []).append(descriptor)

    def _addRegisterDescriptor(self, register: MIPSLocation, descriptor: IdentifierNode):
        self._registerDescriptors.setdefault(register, []).append(descriptor)

    def _overwriteRegisterDescriptors(self, register: MIPSLocation, descriptor: IdentifierNode):
        self._registerDescriptors[register] = [descriptor]

    def _getAssignableAddressDescriptor(self, identifier: IdentifierNode):
        for location in self._addressDescriptors.setdefault(identifier.identifier, []):
            if location.isRegister():
                regDescriptors = self._registerDescriptors[location]
                assert identifier in regDescriptors, f"identifier {identifier.identifier} is supposed to be stored in" \
                                                     f" register {location}, but is not marked as such"
                if len(regDescriptors) == 1:
                    return location
        return None

    def _spillRegister(self, register: MIPSLocation):
        for identifier in self._registerDescriptors[register]:
            # Identifier has spare locations copies, simply disassociate the identifier and register
            if len(self._addressDescriptors[identifier]) > 1:
                self._addressDescriptors[identifier].remove(register)
            if not self.currentSymbolTable[identifier].isFpOffsetInitialized():
                pass


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

    def _getReservedLocation(self, expression: ExpressionNode) -> MIPSLocation:
        return self._reservedLocations[expression.sethiUllmanNumber(self._SUbase)]


    def _getAssignableSavedRegister(self) -> MIPSLocation | None:
        """
        Reserve a single saved register. May spill an in use register
        to obtain the requested register.

        :return: register
        """

        result = ""

        for register in self._savedRegisters:
            if len(self._registerDescriptors[register]) == 0:
                result = register

        if result == "":
            result = self._savedRegisters[-1]
            self._spillRegister(result)

        # TODO move this to visitVar_assig()?
        self._currFuncDef.usedSavedRegisters.add(result)

        return result

    @staticmethod
    def _isExpressionRoot(node: ExpressionNode):
        return not isinstance(node.parent, ExpressionNode)

    def _reserveRegisters(self, amount: int) -> List[MIPSLocation]:
        """
        Reserve :count: temporary and saved registers. There is a preference for
        temporary registers. A lacking number of temporaries is filled out with
        saved registers.

        :param amount: The amount of registers to reserve
        :return: The reserved registers
        """

        reserved = []

        # TODO reserve actual registers
        reserved = self._tempRegisters[:amount]
        # TODO reserve actual registers

        return reserved

    def _addTextLabel(self, labelName: str):
        self._currFuncDef.instructions.append(labelName + ":")

    def _addTextInstruction(self, instruction: str, insertIndex: int = -1):
        instruction = ' ' * 4 + instruction
        if insertIndex >= 0:
            self._currFuncDef.instructions.insert(insertIndex, instruction)
        else:
            self._currFuncDef.instructions.append(instruction)

    def _addTextWhiteSpace(self, instructionIndex: int):
        self._sectionText[instructionIndex] += "\n"

    def _byteSize(self, cType: CType):
        if cType == self.typeList[BuiltinNames.CHAR]:
            return 1
        elif cType == self.typeList[BuiltinNames.INT] or cType == self.typeList[BuiltinNames.FLOAT]:
            return mk.WORD_SIZE

    def _registerIsOccupied(self, register: MIPSLocation):
        return self._registerDescriptors.__contains__(register) and len(self._registerDescriptors[register]) != 0

    def _closeScope(self):
        # Purge all saved register usage information of the current scope
        for identifier in self.currentSymbolTable.mapping.keys():
            for location in self._addressDescriptors.get(identifier, []):
                if location.isRegister():
                    self._registerDescriptors.get(location).remove(identifier)
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
    # registers.
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
        dstIndex = self._SUbase + node.ershovNumber - 1  # The index of the register the result of the bop will be stored in

        # TODO save results before fCall? ==> Backtrack through tree and use ershov
        #   index (b + k - 1), + take big/small child into consideration, to
        #   know which registers to save
        #   1) preallocate save registers by doing a preliminary pass to locate function calls and to store temp registers
        #   2) move temps to saveds when needed
        #   3) move temps to mem when needed ==> !!! increment frame size !!!²

        if lhs.ershovNumber == rhs.ershovNumber:
            self._SUbase += 1  # Increment base recursively for rhs
            rhs.accept(self)
            self._SUbase -= 1  # Decrement base recursively after rhs

            lhs.accept(self)

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

        dstRegister = self._expressionEvalDstReg if self._isExpressionRoot(node) and self._expressionEvalDstReg is not None\
            else self._reservedLocations[dstIndex]
        bopInstruction = f"{mipsKeyword} {dstRegister}, {lhsResult}, {rhsResult}"
        self._addTextInstruction(bopInstruction)

    def visitUnaryexpression(self, node: UnaryexpressionNode):
        node.getSubExpression().accept(self)

    def visitUnaryop(self, node: UnaryopNode):
        # single child, Ershov number remains unchanged

        # +, -, !

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
            self._sectionData.append(f"string{self._stringCounter}: .asciiz \"{output_str}\"" )
            self._addTextInstruction("li $v0, 4")
            self._addTextInstruction(f"la $a0, string{self._stringCounter}")
            self._addTextInstruction("syscall")

        self._currFuncDef.isLeaf = False
        self._currFuncDef.adjustArgumentSlotCount(node)

        # TODO save intermediary results of the expression this function call is a part of

        # Calculate parameters
        paramExpressions = node.getParameterNodes()
        self._reservedLocations = []

        for argIdx, paramExp in enumerate(paramExpressions):
            # TODO reserve registers, reserve registers so that final result stored in $a reg or mem

            paramLoc = self.evaluateExpression(paramExp)

            # TODO store f"$a{argIdx}" into f"{argIdx*mk.WORD_SIZE}($sp)", because stack pointer should be at the end of
            #  the stack frame, which is where the arg slots are located
            # TODO move register resultIndex into $a register or memory

        # Spill convention

        # reclaim spilled registers

        # copy return values (for array $v0 contains ptr to first element and array elements are stored in memory???)

    def visitVar_assig(self, node: Var_assigNode):
        rhs: ExpressionNode = node.getChild(1)
        lhs: IdentifierNode = node.getIdentifierNode()

        if not isinstance(lhs, IdentifierNode):
            raise UnsupportedFeature("The lhs of an assignment must be an identifier for now")

        lhsLoc = self._getAssignableAddressDescriptor(lhs)      # an overwritable register of lhs, else None
        if lhsLoc is None:
            lhsLoc = self._getAssignableSavedRegister()
        rhsLoc = self.evaluateExpression(rhs, resultDstReg=lhsLoc)

        # TODO if lhsLoc is a register that will be used in evaluating the rhs expression,
        #   then the value in its will be lost/changed during the evaluation, making the
        #   result of the evaluation possibly incorrect

        if isinstance(lhs, IdentifierNode):
            # If identifier does not yet have a
            if lhsLoc == "" or lhsLoc.isAddress():
                self._addAddressDescriptor(lhs, rhsLoc)
                self._addRegisterDescriptor(rhsLoc, lhs)
            # All other identifiers making use of lhs' register must have their
            # descriptors changed as well


    def evaluateExpression(self, expression: ExpressionNode, resultDstReg: MIPSLocation | None = None):
        """
        Evaluate the passed expression and return the register containing the final result.
        In the case of a literal that is not the root of an expression, the literal value
        is returned instead.

        :param expression: The expression to evaluate
        :param resultDstReg: A specified location the result of the evaluation should be stored at
        :return: The result of the evaluation
        """

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
                dstRegister = self._getReservedLocation(expression) if resultDstReg is None\
                    else resultDstReg
                self._addTextInstruction(load('I', value, dstRegister))
                value = dstRegister

            dstLoc = value
        # Sub-expression is an identifier
        elif isinstance(expression, IdentifierNode):

            # Ensure that an identifier part of an expression gets loaded
            # into a register
            src: MIPSLocation = self.currentSymbolTable[expression.identifier].register
            if not src.isRegister():
                assert src == "" or src.isAddress(), "Invalid identifier mips location"
                # Prepare load instruction for src
                instrType = "R" + (
                    "B" if expression.inferType(self.typeList) == CharNode.inferType(self.typeList) else "W")
                dstRegister = self._getReservedLocation(expression)\
                    if resultDstReg is None or not self._isExpressionRoot(expression)\
                    else resultDstReg
                comment: str = f"load {expression.identifier}"

                # Using uninitialized variable, allocate stack memory
                if src == "":
                    record = self.currentSymbolTable[expression.identifier]
                    fpOffset = record.fpOffset
                    if not record.isFpOffsetInitialized():
                        fpOffset = self._stackReserve(expression.getType())
                    self.currentSymbolTable[expression.identifier].fpOffset = fpOffset
                    src = constructAddress(fpOffset, mk.FP)

                    # Log assigned stack memory
                    self._addAddressDescriptor(expression, src)

                    comment += " (uninitialized)"

                loadInstr = load(instrType, src, dstRegister, comment)
                self._addTextInstruction(loadInstr)

                self._addAddressDescriptor(expression, dstRegister)
                self.currentSymbolTable[expression.identifier].register = dstRegister

            # Always returns a register
            dstLoc = self.currentSymbolTable[expression.identifier].register
        else:
            # Evaluate the expression
            expression.accept(self)

            dstLoc = self._getReservedLocation(expression)

        # TODO free registers???
        if self._isExpressionRoot(expression):
            pass

        return dstLoc

    def visitIterationstatement(self, node: IterationstatementNode):
        self._openScope(node)
        self._addTextInstruction(f"b $L{self.labelCounter}")
        self._addTextLabel(f"b $L{self.labelCounter + 1}")
        for i in range(1, len(node.children)):
            node.getChild(i).accept(self)
        self._addTextLabel(f"$L{self.labelCounter}")
        result = self.evaluateExpression(node.getChild(0))
        self._addTextLabel(f"bne {result},$0,$L{self.labelCounter + 1}")
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


#########################################
#   MIPS Instruction Creation METHODS   #
#########################################
#


def load(instrType: str, srcAddress, dstReg: MIPSLocation, comment: str = ""):
    if not (instrType == "I" or instrType == "RW" or instrType == "RB" or instrType == "RA"):
        raise Exception("Incorrect mips load type")

    if instrType != "I" and not srcAddress.isAddress():
        raise Exception(f"Loading from incorrect source (should be address): load from '{srcAddress}'")

    if not dstReg.isRegister():
        raise Exception(f"Loading into incorrect destination (should be register): load into '{dstReg}'")

    instruction = mk.I_L if instrType == "I" else \
        (mk.R_LW if instrType == "RW" else (mk.R_LB if instrType == "RB" else mk.R_LA))
    return f"{instruction} {dstReg}, {srcAddress}" + ("" if comment == "" else ('\t' * 2 + MIPSComment(comment)))


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
    return f"{instruction} {src}, {dstReg}" + ("" if comment == "" else ('\t' * 2 + MIPSComment(comment)))


def MIPSComment(text: str):
    return mk.COMMENT_PREFIX + " " + text
