class ASTree:
    def __init__(self, value, name):
        self.value = value  # TODO  delete this, should be in derived classes
        self.children = []
        self.name = name

    def preorderTraverse(self, progress, layer):
        progress.append([self.name, self.value, layer])
        for child in self.children:
            if len(child.children) != 0:
                child.preorderTraverse(progress, layer+1)
            else:
                progress.append([child.name, child.value, layer+1])
        return progress

    def toDot(self):
        file = open("AST.dot", "w")
        file.write("digraph AST {" + '\n')
        traverse = self.preorderTraverse([], 0)
        while len(traverse) != 0:
            root = traverse[0]
            del traverse[0]
            for j in range(len(traverse)):
                if traverse[j][2] == root[2]:
                    break
                if root[2] + 1 == traverse[j][2]:
                    file.write('\t' + '"' + root[0] + "|" + str(root[1]) + '"' +
                               "->" + '"' + traverse[j][0] + "|" + str(traverse[j][1]) + '"' + '\n')

        file.write("}")


