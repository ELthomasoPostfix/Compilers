import sys

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


class Map:
    pass


class FlagContainer:
    """
    A class that makes use of the sys package to check for the presence of
    registered flags amongst the arguments passed to the program, through
    sys.argv.
    """
    def __init__(self):
        self.flags: Dict[str: Set[str]] = {}
        self.explanations: Dict[str: str] = {}

    def reset(self):
        self.flags.clear()

    def registerFlagType(self, flagType: str, flags: Set[str] = None):
        if flags is None:
            flags = {}
        if flagType not in self.flags.keys():
            if flags is None:
                self.flags[flagType] = {}
            else:
                self.flags[flagType] = flags

    def registerFlags(self, flagType: str, flags: Set[str]):
        if flagType in self.flags.keys():
            self.flags[flagType].update(flags)
        else:
            self.registerFlagType(flagType, flags)

    def registerExplanation(self, flagType: str, explanation: str):
        self.explanations[flagType] = explanation

    def getExplanation(self, flagType: str):
        return self.explanations[flagType]

    def checkFlag(self, flagType: str):
        return flagType in self.flags.keys() and self.flags[flagType].intersection(sys.argv)
