# TODO  ask for line nr?
class CCompilerException(Exception):
    def __init__(self, message, location):
        super(CCompilerException, self).__init__ \
            (message + f"\n NOT AGAIN?! HOW MANY TIMES IS THIS GOING TO HAPPEN?! LOOK AT LINE NR{location}")
        self.printmsg = message + f"\nNOT AGAIN?! HOW MANY TIMES IS THIS GOING TO HAPPEN?! LOOK AT :" \
                                  f"\n{{LINE nr. {location[0]}, COLUMN nr. {location[1]}}}  UP TO  " \
                                  f"{{LINE nr. {location[2]}, COLUMN nr. {location[3]}}}"


#########################################
# Declaration and Definition exceptions #
#########################################


class OutOfBoundsLiteral(CCompilerException):
    def __init__(self, message, location):
        super(CCompilerException, self).__init__(message, location)


#########################################
# Declaration and Definition exceptions #
#########################################

class ConstAssigException(CCompilerException):
    pass


class DeclarationException(CCompilerException):
    def __int__(self, message, location):
        super().__init__(message, location)


class RedeclaredSymbol(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str, location):
        super().__init__(f"Redeclaration of known symbol: {identifier}, {oldValue} to {newValue}", location)


class RedefinedFunctionSymbol(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str, location):
        super().__init__(f"Redefinition of known function symbol: {identifier}, {oldValue} to {newValue}", location)


class FunctionTypeMismatch(DeclarationException):
    def __init__(self, identifier: str, oldValue: str, newValue: str, location):
        super().__init__ \
            (f"Redeclaration of known function symbol, return or param type mismatch: {identifier}, {oldValue} to {newValue}",
             location)


class UndefinedFunction(DeclarationException):
    def __init__(self, funcCallRepr: str, location):
        super().__init__(f"Undefined function: function call of {funcCallRepr} references a yet undefined function.", location)


class UndeclaredSymbol(DeclarationException):
    def __init__(self, identifier: str, location):
        super().__init__(f"Unknown symbol: {identifier}", location)


class InitializationException(CCompilerException):
    def __init__(self, message, location):
        super(CCompilerException, self).__init__(message, location)


#######################
# Semantic exceptions #
#######################


class SemanticException(CCompilerException):
    def __int__(self, message, location):
        super().__init__(message, location)


class MisplacedJumpStatement(SemanticException):
    def __init__(self, jumpStatementName: str, properLocation: str, location):
        super().__init__ \
            (f"Misplaced jump statement: a {jumpStatementName} statement should be located within a {properLocation}", location)


class UnknownType(SemanticException):
    def __init__(self, typeName: str, location):
        super().__init__(f"Unknown type: {typeName}", location)


class InvalidReturnStatement(SemanticException):
    def __init__(self, details: str, location):
        super().__init__(f"Invalid return statement: {details}", location)


class InvalidFunctionCall(SemanticException):
    def __init__(self, details: str, location):
        super().__init__(f"Invalid function call: {details}", location)


class InvalidBinaryOperation(SemanticException):
    def __init__(self, operator: str, details: str, location):
        super().__init__(f"Invalid binary {operator}: {details}", location)


class GlobalScopeException(SemanticException):
    def __init__(self, details: str, location):
        super(f"Disallowed at global scope: {details}", location)


##########################
# Compilation exceptions #
##########################


class CompilationException(CCompilerException):
    def __init__(self, message, location):
        super().__init__(message, location)


class UnsupportedFeature(CompilationException):
    def __init__(self, details: str, location):
        super().__init__(f"Unsupported feature: {details}", location)
