import sys
from ctypes import pointer, c_float, POINTER, c_int32, cast, c_char
from typing import List, Set, Dict


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def coloredDef(text):
    return colored(255, 0, 0, text)


def first(items: list, predicate: callable):
    """
    Find the first occurrence in items that satisfies te given predicate.
    :param items: The list to search
    :param predicate: The predicate that must be satisfied
    :return: The first match if found, else None
    """
    return next((item for item in items if predicate(item)), None)


def ftoi(fl: float) -> int:
    """
    Interpret the passed single precision (32-bit) floating point bit sequence as a signed integer.

    :param fl: The to interpret float.
    :return: The integer interpretation.
    """

    return cast(pointer(c_float(fl)), POINTER(c_int32)).contents.value


def isOctalEscapeSequence(octal: str) -> bool:
    if len(octal) < 2 or len(octal) > 4:
        return False
    return octal[0] == '\\' and all('0' <= dig <= '7' for dig in octal[1:])


def isHexEscapeSequence(hex: str) -> bool:
    if len(hex) < 3 or len(hex) > 4:
        return False
    return hex[:2] == "\\x" and all('0' <= dig <= '9' or 'a' <= dig <= 'f' or 'A' <= dig <= 'F' for dig in hex[2:])


def isCharEscapeSequence(char: str) -> bool:
    if len(char) != 2:
        return False
    return char[0] == '\\' and char[1] in "\'\"abfnrtv\\"


def ctoi(c: str) -> int:
    """
    Interpret the signed char bit sequence, octal escape sequence or hex escape sequence as a signed integer.

    :param c: The to interpret char.
    :return: The integer interpretation.
    """

    if isOctalEscapeSequence(c):
        return int(c[1:], 8)
    elif isHexEscapeSequence(c):
        return int(c[2:], 16)
    elif isCharEscapeSequence(c):
        c = bytes(c, "utf-8").decode("unicode_escape")

    assert len(c) == 1
    return ord(c)



class FlagContainer:
    """
    A class that makes use of the sys package to check for the presence of
    registered flags amongst the arguments passed to the python script.
    """
    def __init__(self):
        self.flags: Dict[str: Set[str]] = {}
        self.explanations: Dict[str: str] = {}

    def reset(self):
        """
        Clear the registered flag types and explanations.
        """
        self.flags.clear()
        self.explanations.clear()

    def registerFlagType(self, flagType: str, flags: Set[str] = None):
        """
        Register the flag type and the passed flags to it.
        If the flag type was already registered, then its flags are
        overwritten.
        Only registers flags with the '-' or '--' prefix, others are ignored.
        e.g. registerFlags("help", {'-h', '--help', 'help'})
            which registers '-h' and '--help', but not 'help'
        :param flagType: The alias for the to register flags
        :param flags: The flags to register under :flagType:
        """
        if flags is None:
            flags = {}
        if flagType not in self.flags.keys():
            if flags is None:
                self.flags[flagType] = {}
            else:
                self.flags[flagType] = flags

    def registerFlags(self, flagType: str, flags: Set[str]):
        """
        Register the passed flags to a flag type. An exception of type Exception is raised if
        the specified flag type is not yet registered.
        :param flagType: Under which flag type to register the flags
        :param flags: The flags to register under :flagType:
        """
        flags = {flag for flag in flags if len(flag) >= 2 and (flag[0] == '-' or flag[:2] == '--')}
        if flagType in self.flags.keys():
            self.flags[flagType].update(flags)
        else:
            raise Exception(f"Invalid flag type: cannot register flags {flags} under non-existent flag type '{flagType}'")

    def registerExplanation(self, flagType: str, explanation: str):
        if flagType in self.flags.keys():
            self.explanations[flagType] = explanation
        else:
            raise Exception(f"Invalid flag type: cannot register explanation under non-existent flag type '{flagType}'")

    def getExplanation(self, flagType: str):
        """
        Retrieve the registered explanation of the registered flag type.
        :param flagType: Flag type for which to retrieve explanation
        :return: explanation in string format
        """
        return self.explanations[flagType]

    def checkFlag(self, flagType: str):
        """
        Check whether the registered flag type is present within the script arguments.
        :param flagType: The type of flag to check
        :return: Whether the flag type is found within the script arguments. Defaults to False if type is not registered
        """
        return flagType in self.flags.keys() and self.flags[flagType].intersection(sys.argv)

    @staticmethod
    def argc():
        """
        Get the argument count.
        :return: Argument count
        """
        return len(sys.argv)
