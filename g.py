class G():
    def __init__(self):
        self.nodesList = []
        self.edgesList = []
        self.spawningTree = []
        self.perfectMatchingEdges = []
        self.eulerianCycle = []
        self.bestSolution = 0
        self.solutionsNeighbors = []
        
    def addNode(self, _node):
        self.nodesList.append(_node)
        
    def refreshEdgesList(self):
        self.edgesList = []
        for node in self.nodesList :
            self.edgesList = self.edgesList + node.edgesList 