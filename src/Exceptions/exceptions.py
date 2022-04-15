

# TODO  ask for line nr?
class CCompilerException(Exception):
    pass



class DeclarationException(CCompilerException):
    def __int__(self, message):
        super().__init__(message)


class RedeclaredSymbolException(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str):
        super().__init__(f"Redeclaration of known symbol: {identifier}, {oldValue} to {newValue}")


class UndeclaredSymbolException(DeclarationException):
    def __init__(self, identifier: str):
        super().__init__(f"Unknown symbol: {identifier}")



class InitializationException(CCompilerException):
    pass


