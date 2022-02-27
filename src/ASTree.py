class ASTree:
    def __init__(self, value, name):
        self.value = value  # TODO  delete this, should be in derived classes
        self.children = []
        self.name = name

    def preorderTraverse(self, progress, layer):
        progress.append([self.value, self.name, layer])
        for child in self.children:
            if len(child.children) != 0:
                child.preorderTraverse(progress, layer + 1)
            else:
                progress.append([child.value, child.name, layer + 1])
        return progress

    def toDot(self):
        file = open("AST.dot", "w")
        file.write("digraph AST {" + '\n')
        traverse = self.preorderTraverse([], 0)
        counter = 1
        for i in range(len(traverse)):
            file.write('\t' + "ID" + str(counter) + " [label=" + '"' + str(traverse[i][1]) + " | " +
                       str(traverse[i][0]) + '"' + "]" + '\n')
            counter += 1
        file.write('\n')
        counter = 0
        while len(traverse) != 0:
            root = traverse[counter]
            for j in range(counter, len(traverse)):
                if traverse[j][2] == root[2] and j > counter:
                    break
                if root[2] + 1 == traverse[j][2]:
                    file.write('\t' + "ID" + str(counter + 1) + "->" + "ID" + str(j+1) + '\n')
            counter += 1
            if counter == len(traverse):
                break

        file.write("}")


