from __future__ import annotations
import sys
from typing import List

from src.ASTree.Element import Element


class ASTree(Element):
    def __init__(self, parent=None, location=None):
        self.children: [ASTree] = []
        self.parent: ASTree = parent
        assert(not isinstance(location, int))   #LineNr debug purposes
        self.location: list = location

    def replaceSelf(self, replacement) -> None:
        """
        Replace the caller by the replacement argument in the AST. In other words,
        replace the caller by the replacement argument in all parent-caller and caller-child relationships.
        After the operation is concluded, the caller retains none of its parent and children relations.
        Overwrites all the replacement's parent-replacement and replacement-child relations.
        A notable exception to this overwriting is when the replacement is a child of the caller.
        Then, the old children of the replacement are inserted into the replacement's position as a child.

        :param replacement: The replacement of the caller in the AST. Passing None will essentially clip the caller and all its children from the caller's parent AST.
        """
        if self.parent is not None and self in self.parent.children:
            if replacement is None:
                self.parent.children.remove(self)
            else:
                # Change parent-caller relationship to parent-replacement relationship
                self.parent.children[self.parent.children.index(self)] = replacement
                replacement.parent = self.parent

                # Make replacement adopt caller's children
                from copy import copy
                oldChildren = copy(replacement.children)
                replacement.children = copy(self.children)
                if replacement in replacement.children:     # preserve replacement's old children
                    rIdx = replacement.children.index(replacement)
                    replacement.children = replacement.children[:rIdx] + oldChildren +\
                                           replacement.children[rIdx+1:]

            self.parent = None
            self.children.clear()

    def detachSelf(self) -> ASTree:
        """Undo the caller-parent relationship. The caller is removed a child of the parent."""
        self.parent.children.remove(self)
        self.parent = None
        return self

    def addChild(self, child, idx: int = sys.maxsize) -> ASTree:
        """
        Create a parent child relationship between the child argument and the caller, inserting the
        child at the specified index. Note that if the idx argument is larger than the children list
        size, the child will be appended instead. Negative idx arguments are accepted.
        Returns the added child to allow chaining of calls to construct a vertical branch.

        :param child: The new child of the caller
        :param idx: Insert child at this index
        :return: The added child
        """
        self.children.insert(idx, child)
        child.parent = self
        return child

    def getChild(self, idx: int, wrapAround: bool = True) -> ASTree:
        """
        Get the child at the specified index. If index out of range,
        None is returned instead.
        :param idx: The index of the requested child
        :param wrapAround: Whether negative indexes should wrap around
        :return: The requested child if index in range, else None
        """

        cLen = len(self.children)
        return self.children[idx] if cLen > 0 and idx < cLen and (wrapAround or (not wrapAround and idx >= 0)) else None

    def getSibling(self, offset: int, wrapAround: bool = False):
        """
        Get the sibling :offset: positions from the callee.

        :param offset: The amount of positions to offset from the callee in its parent's children list
        :param wrapAround: Whether out-of-bounds (negative or too large) indexes should wrap around
        :return: The sibling if it exists, else None. Returns None callee has no parent
        """
        if self.parent is None:
            return None

        idx: int = self.parent.children.index(self) + offset
        if wrapAround:
            idx %= len(self.parent.children)
        return self.parent.getChild(idx, wrapAround=wrapAround)

    def getAncestorOfType(self, ancestorType) -> ASTree | None:
        """
        Get the caller's first ancestor of the specified
        type, using isinstance.

        :param ancestorType: The class to check for
        :return: The ancestor if it exists, else None
        """

        if self.parent is None:
            return None
        elif isinstance(self.parent, ancestorType):
            return self.parent
        return self.parent.getAncestorOfType(ancestorType)

    def hasTypeAncestor(self, ancestorType) -> bool:
        """
        Check whether the caller has an ancestor of the specified
        type, using isinstance.

        :param ancestorType: The class to check for
        :return: Result
        """

        return self.getAncestorOfType(ancestorType) is not None

    def preorderTraverse(self, progress, layer) -> List[List[ASTree, int]]:
        progress.append([self, layer])
        for child in self.children:
            if len(child.children) != 0:
                child.preorderTraverse(progress, layer + 1)
            else:
                progress.append([child, layer + 1])
        return progress

    def toDot(self, fileName, detailed: bool = False):
        f = "__repr__" if detailed else "__str__"
        file = open("Output/" + fileName, "w")
        file.write("digraph AST {" + '\n')
        traverse = self.preorderTraverse([], 0)
        counter = 1
        for i in range(len(traverse)):
            file.write(
                '\t' + "ID" + str(counter) + " [label=" + '"' + str(getattr(traverse[i][0], f)()) + '"' + "]" + '\n')
            counter += 1
        file.write('\n')
        counter = 0
        while True:
            root = traverse[counter]
            for j in range(counter, len(traverse)):
                if traverse[j][1] == root[1] and j > counter:
                    break
                if root[1] + 1 == traverse[j][1]:
                    file.write('\t' + "ID" + str(counter + 1) + "->" + "ID" + str(j + 1) + '\n')
            counter += 1
            if counter == len(traverse):
                break

        file.write("}")

    def __repr__(self):
        """
        Return the single ASTree node represented in string format.
        This method should return a detailed representation, read
        minimal representation plus meta info, of the ASTree node.
        :return: detailed string representation
        """
        return self.__str__() + f"\\n l{self.location[0]}c{self.location[1]} to l{self.location[2]}c{self.location[3]}"

    def __str__(self):
        """
        Return the single ASTree node represented in string format.
        This method should return a minimal representation of the ASTree node.
        :return: minimal string representation
        """
        return type(self).__name__

