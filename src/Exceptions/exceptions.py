

# TODO  ask for line nr?
class CCompilerException(Exception):
    pass

#########################################
# Declaration and Definition exceptions #
#########################################


class OutOfBoundsLiteral(CCompilerException):
    pass

#########################################
# Declaration and Definition exceptions #
#########################################


class DeclarationException(CCompilerException):
    def __int__(self, message):
        super().__init__(message)


class RedeclaredSymbol(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str):
        super().__init__(f"Redeclaration of known symbol: {identifier}, {oldValue} to {newValue}")


class RedefinedFunctionSymbol(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str):
        super().__init__(f"Redefinition of known function symbol: {identifier}, {oldValue} to {newValue}")


class FunctionTypeMismatch(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str):
        super().__init__(f"Redeclaration of known function symbol, return or param type mismatch: {identifier}, {oldValue} to {newValue}")


class UndeclaredSymbol(DeclarationException):
    def __init__(self, identifier: str):
        super().__init__(f"Unknown symbol: {identifier}")



class InitializationException(CCompilerException):
    pass

#######################
# Semantic exceptions #
#######################


class SemanticException(CCompilerException):
    def __int__(self, message):
        super().__init__(message)


class MisplacedJumpStatement(SemanticException):
    def __init__(self, jumpStatementName: str, properLocation: str):
        super().__init__(f"Misplaced jump statement: a {jumpStatementName} statement should be located within a {properLocation}")


class UnknownType(SemanticException):
    def __init__(self, typeName: str):
        super().__init__(f"Unknown type: {typeName}")


class InvalidReturnStatement(SemanticException):
    def __init__(self, details: str):
        super().__init__(f"Invalid return statement: {details}")


class InvalidFunctionCall(SemanticException):
    def __init__(self, details: str):
        super().__init__(f"Invalid function call: {details}")


class InvalidBinaryOperation(SemanticException):
    def __init__(self, operator: str, details: str):
        super().__init__(f"Invalid binary {operator}: {details}")

class GlobalScope(SemanticException):
    def __init__(self, details: str):
        super(f"Disallowed at global scope: {details}")

##########################
# Compilation exceptions #
##########################


class CompilationException(CCompilerException):
    def __init__(self, message):
        super().__init__(message)


class UnsupportedFeature(CompilationException):
    def __init__(self, details: str):
        super().__init__(f"Unsupported feature: {details}")
