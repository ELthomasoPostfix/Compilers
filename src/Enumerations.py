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

    CALL: str = "call"
    RETURN: str = "ret"
    ALLOCA: str = "alloca"
    STORE: str = "store"
    LOAD: str = "load"
    FOP_PREF: str = "f"     # float binary prefix
    SOP_PREF: str = "s"     # signed binary prefix
    IOP_PREF: str = "i"     # integer binary prefix
    SUM: str = "add"
    MIN: str = "min"
    MUL: str = "mul"
    DIV: str = "div"
    AND: str = "and"
    OR: str = "or"
    MOD: str = "rem"
    COMPARE: str = "cmp"

    EQ: str = "eq"
    NEQ: str = "neq"
    LT: str = "slt"
    GT: str = "sgt"
    LTE: str = "sle"
    GTE: str = "sge"

    VOID: str = "void"
    I32: str = "i32"
    FLOAT: str = "float"
    CHAR: str = "i8"
    STR: str = f"[n x {CHAR}]"

