import re

from src.CompilersUtils import toCaptureRange


class BuiltinNames:
    VOID: str = "void"
    CHAR: str = "char"
    SHORT: str = "short"
    INT: str = "int"
    LONG: str = "long"
    FLOAT: str = "float"
    DOUBLE: str = "double"


class BuiltinRanks:
    VOID: int = 0
    CHAR: int = 1
    SHORT: int = 2
    INT: int = 3
    LONG: int = 4
    LONG_LONG: int = 5
    FLOAT: int = 6
    DOUBLE: int = 7
    LONG_DOUBLE: int = 8


class LLVMKeywords:
    GLOBAL: str = "global"
    ALIGN: str = "align"
    DEFINE: str = "define"

    BRANCH: str = "br"
    CALL: str = "call"
    RETURN: str = "ret"
    ALLOCA: str = "alloca"
    STORE: str = "store"
    LOAD: str = "load"
    FOP_PREF: str = "f"     # float binary prefix
    SOP_PREF: str = "s"     # signed binary prefix
    IOP_PREF: str = "i"     # integer binary prefix
    SUM: str = "add"
    MIN: str = "sub"
    MUL: str = "mul"
    DIV: str = "div"
    AND: str = "and"
    OR: str = "or"
    MOD: str = "rem"
    COMPARE: str = "cmp"
    FNEG: str = "fneg"

    EQ: str = "eq"
    NEQ: str = "ne"
    LT: str = "slt"
    GT: str = "sgt"
    LTE: str = "sle"
    GTE: str = "sge"

    VOID: str = "void"
    I32: str = "i32"
    I1: str = "i1"
    FLOAT: str = "float"
    CHAR: str = "i8"
    STR: str = f"[n x {CHAR}]"


class MIPSRegisterInfo:
    V_REG_COUNT: int = 2
    A_REG_COUNT: int = 4
    T_REG_COUNT: int = 10
    S_REG_COUNT: int = 8
    F_REG_COUNT: int = 32   # TODO float registers are also divided into v, a, t and s registers. Check MARS editor coprocessor 1 float reg help popups!

    ZERO: str = "$0"
    ZERO_FULL: str = "$zero"
    GP: str = "$gp"
    SP: str = "$sp"
    FP: str = "$fp"
    RA: str = "$ra"

    V_REGEX: str = f"(\\$v{toCaptureRange(V_REG_COUNT - 1)})"
    A_REGEX: str = f"(\\$a{toCaptureRange(A_REG_COUNT - 1)})"
    T_REGEX: str = f"(\\$t{toCaptureRange(T_REG_COUNT - 1)})"
    S_REGEX: str = f"(\\$s{toCaptureRange(S_REG_COUNT - 1)})"
    F_REGEX: str = f"(\\$f{toCaptureRange(F_REG_COUNT - 1)})"
    ZERO_REGEX: str = f"(\\{ZERO}|\\{ZERO_FULL})"
    SPECIAL_REGEX: str = f"({ZERO_REGEX}|\\{GP}|\\{SP}|\\{FP}|\\{RA})"
    REGISTER_REGEX: str = V_REGEX + "|" + A_REGEX + "|" + T_REGEX + "|" + \
                          S_REGEX + "|" + F_REGEX + "|" + SPECIAL_REGEX


class MIPSLocation(str):
    label = "[a-zA-Z._][a-zA-Z0-9._]*"
    posLiteralNum = "(0|[1-9][0-9]*)"
    literalNum = f"-?{posLiteralNum}"

    def __init__(self, value):
        super().__init__()
        self._isRegister: bool = re.fullmatch(MIPSRegisterInfo.REGISTER_REGEX, value) is not None
        self._isAddress:  bool = False
        self._isLabel: bool = re.fullmatch(self.label, value) is not None
        if not self._isRegister:
            # Register contents based address
            #       ($t0)
            #       100($t0)
            #       -100($t0)
            #       label($t0)
            #       label+100($t0)
            if self[-1] == ')' and '(' in self[-7:-4]:
                split = self.split('(')
                registerOffset = split[0]       # The offset to add to the address
                register = split[1][:-1]        # The register containing the address to which to add the offset
                if registerOffset == "" or\
                        re.fullmatch(self.literalNum, registerOffset) is not None or\
                        re.fullmatch(self.label, registerOffset) is not None or\
                        re.fullmatch(f"{self.label}\+{self.posLiteralNum}", registerOffset) is not None:
                    self._isAddress = re.fullmatch(MIPSRegisterInfo.REGISTER_REGEX, register) is not None
            # literal integer or label based address
            #       100
            #       -100
            #       label
            #       label+100               # label-100 is not valid!
            else:
                literalAndLabelRegex = f"{self.literalNum}|{self.label}(\+{self.posLiteralNum})?"

                self._isAddress = re.fullmatch(literalAndLabelRegex, self) is not None

    def isRegister(self):
        return self._isRegister

    def isZeroRegister(self):
        return re.fullmatch(MIPSRegisterInfo.ZERO_REGEX, self) is not None

    def isSavedRegister(self):
        return re.fullmatch(MIPSRegisterInfo.S_REGEX, self) is not None

    def isArgRegister(self):
        return re.fullmatch(MIPSRegisterInfo.A_REGEX, self) is not None

    def isTempRegister(self):
        return re.fullmatch(MIPSRegisterInfo.T_REGEX, self) is not None

    def isValRegister(self):
        return re.fullmatch(MIPSRegisterInfo.V_REGEX, self) is not None

    def isFloatRegister(self):
        return re.fullmatch(MIPSRegisterInfo.F_REGEX, self) is not None

    def isAddress(self):
        return self._isAddress

    def isLabel(self):
        return self._isAddress



class MIPSKeywords:
    DATA_DATA: str = ".data"
    DATA_BYTE: str = ".byte"
    DATA_WORD: str = ".word"
    DATA_FLOAT: str = ".float"
    DATA_ASCII: str = ".ascii"
    DATA_ASCIIZ: str = ".asciiz"
    TEXT: str = ".text"
    COMMENT_PREFIX: str = "#"
    WS: str = " " * 4

    ZERO: MIPSLocation = MIPSLocation("$0")
    ZERO_FULL: MIPSLocation = MIPSLocation("$zero")
    GP: MIPSLocation = MIPSLocation("$gp")
    SP: MIPSLocation = MIPSLocation("$sp")
    FP: MIPSLocation = MIPSLocation("$fp")
    RA: MIPSLocation = MIPSLocation("$ra")

    WORD_SIZE: int = 4                  # word size in bytes
    BYTE_SIZE: int = 1                  # byte size in bytes
    REGISTER_SIZE: int = WORD_SIZE      # register size in bytes

    R_ADD: str = "add"
    I_ADD: str = "addi"
    I_ADD_U: str = "addiu"
    R_MIN: str = "sub"
    I_MIN: str = "subi"
    I_MIN_U: str = "subiu"
    S_MUL_N: str = "mul"   # multiplication without overflow
    S_MUL_O: str = "mult"
    S_DIV: str = "div"
    S_REM: str = "rem"
    R_AND: str = "and"
    I_AND: str = "andi"
    R_OR: str = "or"
    I_OR: str = "ori"
    GT: str = "sgt"
    GTE: str = "sge"
    R_LT: str = "slt"
    I_LT: str = "slti"
    LTE: str = "sle"
    NEG: str = "neg"
    NOT: str = "sltiu"  # logical not: !x with x in $t0 == sltiu $t0, $t0, 1

    I_L: str = "li"
    R_LW: str = "lw"
    R_LB: str = "lb"
    R_LA: str = "la"
    R_SW: str = "sw"
    R_SB: str = "sb"

    JR: str = "jr"
    JAL: str = "jal"

    R_MOVE: str = "move"

    @staticmethod
    def getArgRegisters():
        return [MIPSLocation(f"$a{num}") for num in range(MIPSRegisterInfo.A_REG_COUNT)]

    @staticmethod
    def getTempRegisters():
        return [MIPSLocation(f"$t{num}") for num in range(MIPSRegisterInfo.T_REG_COUNT)]

    @staticmethod
    def getSavedRegisters():
        return [MIPSLocation(f"$s{num}") for num in range(MIPSRegisterInfo.S_REG_COUNT)]

    @staticmethod
    def getVarRegisters():
        return [MIPSLocation(f"$v{num}") for num in range(MIPSRegisterInfo.V_REG_COUNT)]


