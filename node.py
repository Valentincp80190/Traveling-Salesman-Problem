class Node():
    def __init__(self, _id, _x, _y):
        self.id = _id
        self.x = _x 
        self.y = _y
        self.root = self
        self.edgesList = []