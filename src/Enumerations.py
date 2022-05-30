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
    NEQ: str = "neq"
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

    V_CAPTURE_REGEX: str = f"(\\$v{toCaptureRange(V_REG_COUNT - 1)})"
    A_CAPTURE_REGEX: str = f"(\\$a{toCaptureRange(A_REG_COUNT - 1)})"
    T_CAPTURE_REGEX: str = f"(\\$t{toCaptureRange(T_REG_COUNT - 1)})"
    S_CAPTURE_REGEX: str = f"(\\$s{toCaptureRange(S_REG_COUNT - 1)})"
    F_CAPTURE_REGEX: str = f"(\\$f{toCaptureRange(F_REG_COUNT - 1)})"
    ZERO_CAPTURE_REGEX: str = f"(\\{ZERO}|\\{ZERO_FULL})"
    SPECIAL_CAPTURE_REGEX: str = f"({ZERO_CAPTURE_REGEX}|\\{GP}|\\{SP}|\\{FP}|\\{RA})"
    REGISTER_CAPTURE_REGEX: str = V_CAPTURE_REGEX + "|" + A_CAPTURE_REGEX + "|" + T_CAPTURE_REGEX + "|" +\
                                  S_CAPTURE_REGEX + "|" + F_CAPTURE_REGEX + "|" + SPECIAL_CAPTURE_REGEX


class MIPSLocation(str):
    def isRegister(self):
        return re.fullmatch(MIPSRegisterInfo.REGISTER_CAPTURE_REGEX, self) is not None

    def isZeroRegister(self):
        return re.fullmatch(MIPSRegisterInfo.ZERO_CAPTURE_REGEX, self) is not None

    def isSavedRegister(self):
        return re.fullmatch(MIPSRegisterInfo.S_CAPTURE_REGEX, self) is not None

    def isArgRegister(self):
        return re.fullmatch(MIPSRegisterInfo.A_CAPTURE_REGEX, self) is not None

    def isTempRegister(self):
        return re.fullmatch(MIPSRegisterInfo.T_CAPTURE_REGEX, self) is not None

    def isValRegister(self):
        return re.fullmatch(MIPSRegisterInfo.V_CAPTURE_REGEX, self) is not None

    def isFloatRegister(self):
        return re.fullmatch(MIPSRegisterInfo.F_CAPTURE_REGEX, self) is not None

    def isAddress(self):
        label = "[a-zA-Z._][a-zA-Z0-9._]*"
        posLiteralNum = "(0|[1-9][0-9]*)"
        literalNum = f"-?{posLiteralNum}"

        if self[-1] == ')' and '(' in self[-7:-4]:
            split = self.split('(')
            if re.fullmatch(literalNum, split[0]) is None and re.fullmatch(label, split[0]) is None and\
                re.fullmatch(f"{label}\+{posLiteralNum}", split[0]) is None:
                return False
            return re.fullmatch(MIPSRegisterInfo.REGISTER_CAPTURE_REGEX, split[1][:-1]) is not None

        regex = f"{literalNum}|{label}|{label}\+{posLiteralNum}"

        return re.fullmatch(regex, self) is not None



class MIPSKeywords:
    DATA: str = ".data"
    TEXT: str = ".text"

    ZERO: MIPSLocation = MIPSLocation("$0")
    ZERO_FULL: MIPSLocation = MIPSLocation("$zero")
    GP: MIPSLocation = MIPSLocation("$gp")
    SP: MIPSLocation = MIPSLocation("$sp")
    FP: MIPSLocation = MIPSLocation("$fp")
    RA: MIPSLocation = MIPSLocation("$ra")

    WORD_SIZE: int = 4          # word size in bytes
    REGISTER_SIZE: int = 4      # register size in bytes

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
        return [MIPSLocation(f"$a{num}") for num in range(MIPSRegisterInfo.A_REG_COUNT).__reversed__()]

    @staticmethod
    def getTempRegisters():
        return [MIPSLocation(f"$t{num}") for num in range(MIPSRegisterInfo.T_REG_COUNT).__reversed__()]

    @staticmethod
    def getSavedRegisters():
        return [MIPSLocation(f"$s{num}") for num in range(MIPSRegisterInfo.S_REG_COUNT).__reversed__()]

    @staticmethod
    def getVarRegisters():
        return [MIPSLocation(f"$v{num}") for num in range(MIPSRegisterInfo.V_REG_COUNT).__reversed__()]


