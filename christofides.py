from time import time

def Kruskal(_graph): #Permet de générer un arbre couvrant minimal
    arcsKruskal = []
    _graph.refreshEdgesList()
    _graph.edgesList = sorted(_graph.edgesList, key=lambda x: x.cost)
    
    for edge in _graph.edgesList :
        if edge.startNode.root == edge.finishNode.root : continue
        nodes = [x for x in _graph.nodesList if x.root == edge.finishNode.root]
        for node in nodes : node.root = edge.startNode.root
        arcsKruskal.append(edge)
    return arcsKruskal

def christofides(_graph):
    currentTime = time()
    minimum_spawning_tree = Kruskal(_graph)