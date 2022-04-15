from __future__ import annotations
from abc import ABCMeta
from typing import List, Union

from src.Exceptions.exceptions import RedeclaredSymbolException


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

    def __repr__(self):
        return self.typeList.__repr__()


## Abstract base class representing type information for symbols in a symbol table.
#
#
class CType:   # TODO  and arrays ?????
    """Abstract base class representing type information for symbols in a symbol table."""
    __metaclass__ = ABCMeta

    def __init__(self):
        self._pointers: List[bool] = []

    ## Add a level of indirection to the CType, possibly marked const through the isConst parameter.
    #
    # It returns self to allow chaining the method.
    def addPointer(self, isConst: bool) -> CType:
        """
        Add a level of indirection to the CType.
        :param isConst: make level of indirection read-only
        :return: self, to allow chaining the method
        """
        self._pointers.append(isConst)
        return self

    def isPointerType(self):
        return len(self._pointers) > 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "".join(["*" + ("const " if const else "") for const in self._pointers])


class VariableCType(CType):
    """A class representing type information for a variable."""
    def __init__(self, typeIndex: int):
        super().__init__()
        self.typeIndex = typeIndex
        self.register = None

    def __str__(self):
        return str(self.typeIndex) + " " + super().__str__()

# TODO   Add LiteralCType class, to be returned by LiteralNode classes????


class FunctionCType(CType):     # TODO:  Are param type needed here? Can't they be inferred from the AST? If not, then FunctionCType can be reduced to VariableType, so better rename VariableType or just move VariableType functionality up into CType
    """A class representing type information for a function."""
    def __init__(self, returnType: int):
        super().__init__()
        self.returnTypeIndex: int = returnType
        self.paramTypes: List[CType] = []

    def __str__(self):
        return str(self.paramTypes) + " -> " + str(self.returnTypeIndex) + " " + super().__str__()




class Record:
    def __init__(self, cType: CType, access: Accessibility):
        self.type: CType = cType
        self.access = access

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str([self.type, self.access])




class SymbolTable(dict):
    """
    An implementation of a symbol table. Each symbol table contains
    a reference to the symbol table of its enclosing scope, which is
    None for the global symbol table.
    As this class inherits from the dict builtin type, the [] operator
    should be similarly used in reading and registering symbols.
    """
    def __init__(self, enclosingScope, typeList):
        super().__init__()
        self._enclosingScope: SymbolTable = enclosingScope
        self.typeList = typeList

    def __getitem__(self, identifier: str) -> Record:
        """Retrieve the symbol table information related to :identifier:.
         Returns None if :identifier: is not declared in the root SymbolTable."""
        if identifier in self:
            return super().__getitem__(identifier)
        if self._enclosingScope is not None:
            return self._enclosingScope[identifier]
        return None

    def __setitem__(self, key: str, value: Record):
        """Register the identifier and its information in the symbol table.
        Raises an exception of type Exception if :identifier: is already registered."""
        lookup = self[key]
        if lookup is not None:
            raise RedeclaredSymbolException(key, str(lookup), str(value))
        super().__setitem__(key, value)

    @property
    def enclosingScope(self):
        return self._enclosingScope
