class ASTree:
    def __init__(self, value, name):
        self.value = value  # TODO  delete this, should be in derived classes
        self.children = []
        self.name = name


    def toDot(self):
        pass

    def inorderTraverse(self, progress):
        if len(self.children) == 0:
            progress.append([self.name, self.value])
            return progress
        else:
            for child in self.children:
                pass

