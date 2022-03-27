import sys
from src.ASTree.Element import Element


class ASTree(Element):
    def __init__(self, value, name, parent=None):
        self.value = value  # TODO  delete this, should be in derived classes
        self.children: [ASTree] = []
        self.name = name
        self.parent: ASTree = parent

    def replaceSelf(self, replacement):
        """
        Replace the caller by the replacement argument in the AST. In other words,
        replace the caller by the replacement argument in all parent-caller and caller-child relationships.
        After the operation is concluded, the caller retains none of its parent and children relations.
        :param replacement: The replacement of the caller in the AST. Passing None will essentially
        clip the caller and all its children from the caller's parent AST.
        """
        if self in self.parent.children:
            self.parent.children[self.parent.children.index(self)] = replacement

            if replacement is not None:
                replacement.parent = self.parent
                replacement.children = self.children

            self.parent = None
            self.children.clear()

    def addChild(self, child, idx: int = sys.maxsize):
        """
        Create a parent child relationship between the child argument and the caller, inserting the
        child at the specified index. Note that if the idx argument is larger than the children list
        size, the child will be appended instead. Negative idx arguments are accepted.
        :param child: The new child of the caller
        :param idx: Insert child at this index
        """
        self.children.insert(idx, child)
        child.parent = self

    def getChild(self, idx: int):
        """
        Get the child at the specified index. If index out of range,
        None is returned instead.
        :param idx: The index of the requested child
        :return: The requested child if index in range, else None
        """
        return self.children[idx] if idx < len(self.children) else None

    def preorderTraverse(self, progress, layer):
        progress.append([self, layer])
        for child in self.children:
            if len(child.children) != 0:
                child.preorderTraverse(progress, layer + 1)
            else:
                progress.append([child, layer + 1])
        return progress

    def toDot(self, fileName):
        file = open("Output/" + fileName, "w")
        file.write("digraph AST {" + '\n')
        traverse = self.preorderTraverse([], 0)
        counter = 1
        for i in range(len(traverse)):
            file.write('\t' + "ID" + str(counter) + " [label=" + '"' + str(traverse[i][0].__repr__()) + '"' + "]" + '\n')
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
        return type(self).__name__
