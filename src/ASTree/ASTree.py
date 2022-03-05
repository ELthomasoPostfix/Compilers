from src.ASTree.Element import Element


class ASTree(Element):
    def __init__(self, value, name):
        self.value = value  # TODO  delete this, should be in derived classes
        self.children = []
        self.name = name

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
            file.write('\t' + "ID" + str(counter) + " [label=" + '"' + str(traverse[i][0].name) + " | " +
                       str(traverse[i][0].value) + '"' + "]" + '\n')
            counter += 1
        file.write('\n')
        counter = 0
        while True:
            root = traverse[counter]
            for j in range(counter, len(traverse)):
                if traverse[j][1] == root[1] and j > counter:
                    break
                if root[1] + 1 == traverse[j][1]:
                    file.write('\t' + "ID" + str(counter + 1) + "->" + "ID" + str(j+1) + '\n')
            counter += 1
            if counter == len(traverse):
                break

        file.write("}")

    def __repr__(self):
        return self.name + " | " + str(self.value)

