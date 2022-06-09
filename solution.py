import math

class Solution():
    def __init__(self, _hamiltonianCycleNodes, _hamiltonianCycleEdges, _cost):
        self.hamiltonianCycleNodes = _hamiltonianCycleNodes
        self.hamiltonianCycleEdges = _hamiltonianCycleEdges
        self.cost = _cost
    
    def updateCost(self):
        cost = 0
        for edge in self.hamiltonianCycleEdges:
            cost = cost + math.sqrt(math.pow(edge.startNode.x - edge.finishNode.x, 2) + math.pow(edge.startNode.y - edge.finishNode.y, 2))
            
        self.cost = cost