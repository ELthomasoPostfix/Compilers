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


class MIPSLocation(str):
    def isRegister(self):
        return self[0] == '$'

    def isAddress(self):
        return False


class MIPSKeywords:
    DATA: str = ".data"
    TEXT: str = ".text"

    ZERO: str = "$0"
    ZERO_FULL: str = "$zero"
    GP: str = "$gp"
    SP: str = "$sp"
    FP: str = "$fp"
    RA: str = "$ra"
    V_REG_COUNT: int = 2
    A_REG_COUNT: int = 4
    T_REG_COUNT: int = 10
    S_REG_COUNT: int = 8
    F_REG_COUNT: int = 32   # TODO float registers are also divided into v, a, t and s registers. Check MARS editor coprocessor 1 float reg help popups!
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

    R_MOVE: str = "move"

    @staticmethod
    def getArgRegisters():
        return [MIPSLocation(f"$a{num}") for num in range(MIPSKeywords.A_REG_COUNT).__reversed__()]

    @staticmethod
    def getTempRegisters():
        return [MIPSLocation(f"$a{num}") for num in range(MIPSKeywords.T_REG_COUNT).__reversed__()]

    @staticmethod
    def getSavedRegisters():
        return [MIPSLocation(f"$a{num}") for num in range(MIPSKeywords.S_REG_COUNT).__reversed__()]

    @staticmethod
    def getVarRegisters():
        return [MIPSLocation(f"$a{num}") for num in range(MIPSKeywords.V_REG_COUNT).__reversed__()]


