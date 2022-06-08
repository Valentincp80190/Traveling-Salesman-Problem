class Edge():
    def __init__(self, _startNode, _finishNode, _cost):
        self.startNode = _startNode
        self.finishNode = _finishNode
        self.cost = _cost
        
    def getCost(self):
        return self.cost