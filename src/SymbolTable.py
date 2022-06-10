from __future__ import annotations
from abc import ABCMeta
from typing import List, Union

from src.Exceptions.exceptions import RedeclaredSymbol, RedefinedFunctionSymbol, FunctionTypeMismatch


class Accessibility(int):
    """Abstract base class representing accessibility for symbols in a symbol table."""
    __metaclass__ = ABCMeta

    def __eq__(self, other):
        """Check equality for subclasses of Accessibility."""
        return isinstance(other, Accessibility) and super().__eq__(other)


class ReadAccess(Accessibility):
    """A class representing read access for a symbol in a symbol table."""
    def __new__(cls, *args, **kwargs):
        return super(ReadAccess, cls).__new__(cls, 1)

    def __repr__(self):
        return "r"


class ReadWriteAccess(Accessibility):
    """A class representing read write access for a symbol in a symbol table."""
    def __new__(cls, *args, **kwargs):
        return super(ReadWriteAccess, cls).__new__(cls, 0)

    def __repr__(self):
        return "rw"




class TypeList:
    """A class that stores all type names to reference using indexes in the symbol table."""
    def __init__(self, initList: List[str]):
        self.typeList = initList
        self.reverseMapping: dict = {typ: idx for idx, typ in enumerate(self.typeList)}

    def __getitem__(self, key: Union[int, str]):
        """
        Retrieve either the type name corresponding to the passed index or the index corresponding
        to the passed type name.
        :param key: Index of a type name or a type name
        :return: Type name, index or None as a default
        """
        if isinstance(key, int):
            return self.typeList[key]
        elif isinstance(key, str):
            return self.reverseMapping[key]
        else:
            return None

    def append(self, newType: str):
        """
        Append a new type to the TypeList. If the type already exists,
         an exception of type Exception is raised.
        :param newType: The type to append
        """
        if newType in self.reverseMapping:
            raise Exception(f"The type {newType} is already a registered type")
        else:
            self.reverseMapping[newType] = len(self.typeList)
            self.typeList.append(newType)

    def __len__(self):
        return len(self.typeList)

    def __repr__(self):
        return self.typeList.__repr__()


## A class representing type information for a variable.
#
#
class CType:
    """A class representing type information for a variable."""

    def __init__(self, typeIndex: int, isArray: bool = False):
        super().__init__()
        self.typeIndex = typeIndex
        self.isArray = isArray
        self._pointers: List[bool] = []

    ## Add a level of indirection to the CType, possibly marked const through the isConst parameter.
    #
    # It returns the caller to allow chaining the method.
    def addPointer(self, isConst: bool) -> CType:
        """
        Add a level of indirection to the CType.

        :param isConst: Make level of indirection read-only or not
        :return: caller, to allow chaining the method
        """
        self._pointers.append(isConst)
        return self

    ## Remove a level of indirection from the CType.
    #
    # It returns the caller to allow chaining the method.
    def removePointer(self) -> CType:
        """
        Remove a level of indirection from the CType.

        :return: caller, to allow chaining the method
        """

        if self.pointerCount() == 0:
            return self

        self._pointers.remove(self._pointers[-1])
        return self

    def pointerCount(self):
        return len(self._pointers)

    def isPointerType(self):
        return self.pointerCount() > 0

    def isConst(self, ptrIndex: int):
        return self._pointers[ptrIndex]

    def typeName(self, typeList: TypeList):
        return typeList[self.typeIndex]

    # def functionCType(self, ):


    def __eq__(self, other, requirePointerEq: bool = False):
        """
        Equality check with :other:.
        Checks type equality.
        Checks pointer equality if :requirePointerEq: is true.
        """

        return ((isinstance(other, int) and other == self.typeIndex) or
                (isinstance(other, CType) and self.typeIndex == other.typeIndex)) and \
               (not requirePointerEq or (requirePointerEq and self._pointers == other._pointers))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.typeIndex) +\
               (" " if self.pointerCount() > 0 else "") + "".join(["*" + ("const " if const else "") for const in self._pointers]) + \
               (" []" if self.isArray else "")


class FunctionCType(CType):
    """A class representing type information for a function."""

    def __init__(self, returnType: int, isDefinition: bool):
        super().__init__(returnType, False)
        self.paramTypes: List[CType] = []
        self.isDefinition: bool = isDefinition

    def __eq__(self, other, requirePointerEq: bool = False, requireParamsEq: bool = False):
        """
        Equality check with :other:. :other: must also be a CType derivative.
        Checks type (return type if :other: is a function type) equality
        Checks parameter equality if :requireParamsEq: is true.
        Checks pointer equality.
        """

        return (not requireParamsEq or
                (requireParamsEq and isinstance(other, FunctionCType) and self.paramTypes == other.paramTypes)) and \
               super().__eq__(other, requirePointerEq)

    def __str__(self):
        return str(self.paramTypes) + " -> " + str(self.typeIndex) + " " + super().__str__()



class MIPSLocation:
    pass


class Record:
    def __init__(self, cType: CType, access: Accessibility):
        self.type: CType = cType
        self.access = access
        self.register: str | MIPSLocation = ""
        self.fpOffset: int = -1     # Offset of the allocated stack memory to the frame pointer

    def __repr__(self):
        return str([self.type, self.access, self.register])

    def __str__(self):
        return str([self.type, self.access])




class SymbolTable:
    """
    An implementation of a symbol table. Each symbol table contains
    a reference to the symbol table of its enclosing scope, which is
    None for the global symbol table.
    As this class inherits from the dict builtin type, the [] operator
    should be similarly used in reading and registering symbols.
    """
    def __init__(self, enclosingScope, typeList):
        super().__init__()
        self._enclosingScope: SymbolTable | None = enclosingScope
        self.mapping: dict = {}
        self.typeList: TypeList = typeList

    def _getScope(self, symbol: str) -> SymbolTable | None:
        """
        Retrieve the SymbolTable the information related to :symbol: is stored in.
        Returns None if :symbol: an unknown symbol.

        :param symbol: The symbol to find the scope of
        :return: The scope of the :symbol:
        """

        if symbol in self.mapping:
            return self
        if self._enclosingScope is not None:
            return self._enclosingScope._getScope(symbol)
        return None

    def __getitem__(self, symbol: str) -> Record | None:
        """
        Retrieve the symbol table information related to :symbol:.
        Returns None if :symbol: an unknown symbol.

        :return: Record for the given symbol
        """

        scope = self._getScope(symbol)
        return None if scope is None else scope.mapping[symbol]

    def __setitem__(self, key: str, value: Record) -> None:
        """
        Register the symbol and its information in the symbol table.
        Raises an exception of type RedeclaredSymbol if :symbol: is already registered.
        """

        lookup = self[key]
        if lookup is not None:
            # Function exclusive declaration errors
            if isinstance(value.type, FunctionCType) and isinstance(lookup.type, FunctionCType):
                if lookup.type.isDefinition and value.type.isDefinition:
                    raise RedefinedFunctionSymbol(key, str(lookup), str(value))
                elif not lookup.type.__eq__(value.type, requireParamsEq=True):
                    raise FunctionTypeMismatch(key, str(lookup), str(value))
            # Variable involved type errors
            elif not (self.isGlobal(key) and self._enclosingScope is not None):
                raise RedeclaredSymbol(key, str(lookup), str(value))

        self.mapping[key] = value

    def isGlobal(self, symbol: str) -> bool:
        """
        Check whether the latest registration of :symbol: is registered at the global
        scope. Because global symbol declarations or definitions do not clash with
        local declarations or definitions, it is possible that even though False is
        returned, there may exist a global definition of symbol, though it is inaccessible
        in the current context.

        :param symbol: The accessible symbol to check global registration of
        :return: result of the check
        """

        scope = self._getScope(symbol)
        return False if scope is None or scope._enclosingScope is not None else True

    def isLocal(self, symbol: str):
        """
        Check whether the symbol is defined within the callee symbol table. Does not
        take enclosing scopes into account.

        :param symbol: The symbol to check local registration for.
        :return: True if symbol is registered in the callee, False if not
        """

        return symbol in self.mapping

    def isGlobalScope(self):
        """
        Check whether the SymbolTable is the global symbol table.

        :return: True if global
        """

        return self._enclosingScope is None

    def setEnclosingScope(self, enclosingScope: SymbolTable):
        self._enclosingScope = enclosingScope

    @property
    def enclosingScope(self):
        return self._enclosingScope

    def __str__(self):
        return self.mapping.__str__()

