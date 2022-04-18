

# TODO  ask for line nr?
class CCompilerException(Exception):
    pass



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



class SemanticException(CCompilerException):
    def __int__(self, message):
        super().__init__(message)


class MisplacedJumpStatement(SemanticException):
    def __init__(self, jumpStatementName: str, properLocation: str):
        super().__init__(f"Misplaced jump statement: a {jumpStatementName} statement should be located within a {properLocation}")

