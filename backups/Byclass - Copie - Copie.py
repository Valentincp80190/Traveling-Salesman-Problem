from asyncio.windows_events import INFINITE, NULL
import math
from time import time
import tkinter as tk
from tkinter import HORIZONTAL, VERTICAL, Label, StringVar, ttk, colorchooser
import os
from os import walk
import pandas as pd
import numpy as np
#utiliser la librarie Pandas table sous forme id / x / y
root = tk.Tk()

#Application du theùe
style = ttk.Style(root)
style.theme_use('winnative')

root['bg']='white'
root.title("Traveling Salesman Problem")
root.resizable(0, 0)

tk.Label(root, text="Benchmarks", bg="white").grid(column=0, row=0)
tk.Label(root, text="Simulation", bg="white").grid(column=2, row=0)
tk.Label(root, text="Configuration", bg="white").grid(column=3, row=0)

listbox = tk.Listbox(root)
scrollbarV = tk.Scrollbar(root, orient=VERTICAL)
scrollbarH = tk.Scrollbar(root, orient=HORIZONTAL)
scrollbarV.grid(column=1, row=1, sticky="ns")
scrollbarH.grid(column=0, row=2, sticky="ew")
listbox.grid(column=0, row=1, sticky="nsew") # north + east [...]
listbox.config(yscrollcommand=scrollbarV.set)
listbox.config(xscrollcommand=scrollbarH.set)
scrollbarV.config(command=listbox.yview)
scrollbarH.config(command=listbox.xview)

cost_text = StringVar()
progressbar_label = Label(root, textvariable=cost_text, bg="white").grid(column=2, columnspan=1, row=3)

progressbar_text = StringVar()
progressbar_label = Label(root, textvariable=progressbar_text, bg="white").grid(column=0, columnspan=3, row=4)
progressbar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=850).grid(column=0, columnspan=4, row=5, sticky="we")

canvasHeight = 600
canvasWidth = 700
canvas = tk.Canvas(root, bg="#202020", height=canvasHeight, width=canvasWidth)
canvas.grid(column=2, row=1)

script_dir = os.path.dirname(__file__) # Récupérer le chemin relatif au script
rel_path = "benchmarks"
abs_file_path = os.path.join(script_dir, rel_path) #Trouve le chemin absolu du dossier benchmarks

configuration = tk.Frame(root, bg="#FFFFFF")
configuration.grid(column=3, row=1, sticky="nes")

filenames = []
#nodes = pd.DataFrame(columns=["x","y","root"])
nodes = np.empty((0,3), np.float64)
arcs = np.empty((0,3), np.float64)
allArcs = arcs




graphList = []

class Client():
    def __init__(self):
        self.displayNodes = tk.BooleanVar(root, True) 
        self.displayEdges = tk.BooleanVar(root, True)
        self.edgeSize = tk.DoubleVar(root, 1) 
        self.nodesColorCode = ((255,0,0), '#FF0000')
        self.edgesColorCode = ((255,255,255), '#FFFFFF')
        self.demoMode = tk.BooleanVar(root, False) 
        
    def selectNodesColor(self):
        self.nodesColorCode = colorchooser.askcolor(title ="Choose nodes color")
        
    def selectEdgesColor(self):
        self.edgesColorCode = colorchooser.askcolor(title ="Choose edges color") 
client = Client()

class G():
    def __init__(self):
        self.nodesList = []
        self.edgesList = []
        self.spawningTree = []
        self.perfectMatchingEdges = []
        
    def addNode(self, _node):
        self.nodesList.append(_node)
        
    def refreshEdgesList(self):
        self.edgesList = []
        for node in self.nodesList :
            self.edgesList = self.edgesList + node.edgesList 
    
class Edge():
    def __init__(self, _startNode, _finishNode, _cost):
        self.startNode = _startNode
        self.finishNode = _finishNode
        self.cost = _cost
        
    def getCost(self):
        return self.cost
        
class Node():
    def __init__(self, _id, _x, _y):
        self.id = _id
        self.x = _x 
        self.y = _y
        self.root = self
        self.edgesList = []

def filesList():
    global filenames
    filenames = next(walk(abs_file_path), (None, None, []))[2] #Parcours les fichiers de haut en bas dans un dossier
    filenames = [ file for file in filenames if file.endswith(".tsp") ] #Exclu les mauvaises extensions

    for filename in filenames: #Inject dans la liste à afficher les noms sans leur extensions
        listbox.insert(tk.END, filename[:filename.index('.')])

def readfile(benchmark):
    global graphList
    currentTime = time()
    file = open(abs_file_path + "/" + filenames[benchmark], "r")
    
    #updateProgressBar(20, "Loading file...")
    i = 0
    for line in file:
        if i == 4:
            line = line.replace(' ', '')
            line = line.replace('EDGE_WEIGHT_TYPE:', '')
            line = line.replace('\n','')
            if line != "EUC_2D":
                canvas.create_text(350,300, text="BENCHMARK NOT COMPATIBLE", fill="#FF0000")
                #updateProgressBar(0, " ")
                return False
            else : graphList.append(G())
            
        if i > 5:
            line = line.split(" ")
            try:
                line[2] = line[2].replace('\n', '')
                graphList[0].addNode(Node(len(graphList[0].nodesList), float(line[1]), float(line[2])))
            except IndexError:
                break
        i = i + 1
    file.close
    print("Loading file time : " + str(time() - currentTime) + ".")
    return True
    
def loadFullGraphArcs(_graph):
    currentTime = time()
    #updateProgressBar(30, "Creation of graph arcs...")  
    #Calcul du poids de tous les arcs pour avoir un graph complet
    nodesList = _graph.nodesList
    for startNode in nodesList :
        for finishNode in nodesList :
            if startNode == finishNode : continue
            #if finishNode in nodesList.edgesList and startNode in nodesList.edgesList : continue
            cost = math.sqrt(math.pow(startNode.x - finishNode.x, 2) + math.pow(startNode.y - finishNode.y, 2))
            startNode.edgesList.append(Edge(startNode, finishNode, cost))
            
    print("Completed graph time : " + str(time() - currentTime) + ".")
    
def Kruskal(_graph): #Permet de générer un arbre couvrant minimal
    #updateProgressBar(60, "Minimum spanning tree generation...")
    #arcs = arcs.sort_values(by=['cost'])
    currentTime = time()
    arcsKruskal = []
    _graph.refreshEdgesList()
    _graph.edgesList = sorted(_graph.edgesList, key=lambda x: x.cost)
    
    for edge in _graph.edgesList :
        if edge.startNode.root == edge.finishNode.root : continue
        #alreadyExistEdge = len([x for x in arcsKruskal if (x.startNode == edge.finishNode and x.finishNode == edge.startNode)])
        #if alreadyExistEdge > 0 : continue
        
        #Union
        #Pour tous noeuds ayant comme root edge.finishNode.root, leur attribuer le root de edge.startNode.root
        nodes = [x for x in _graph.nodesList if x.root == edge.finishNode.root]
        
        for node in nodes :
            node.root = edge.startNode.root
            
        arcsKruskal.append(edge)
    
    print("Minimum spawning tree time : " + str(time() - currentTime) + ".")
    return arcsKruskal

def drawEdges(_graph, _edges, color):
    maxX = sorted(_graph.nodesList, key=lambda x: x.x)[len(_graph.nodesList) - 1].x# = canvasWidth (prend le maximum x des noeuds du graph )
    maxY = sorted(_graph.nodesList, key=lambda x: x.y)[len(_graph.nodesList) - 1].y# = canvasHeight (prend le maximum y des noeuds du graph )
    
    #Représentation des arcs    
    #updateProgressBar(80, "Preparing to display graph arcs...")
    
    for edge in _edges :
        x1 = (edge.startNode.x*canvasWidth)/maxX
        y1 = (edge.startNode.y*canvasHeight)/maxY
        x2 = (edge.finishNode.x*canvasWidth)/maxX
        y2 = (edge.finishNode.y*canvasHeight)/maxY
        canvas.create_line(x1,y1,x2,y2, fill=color, width=client.edgeSize.get())

def drawNodes(_graph, color):
    maxX = sorted(_graph.nodesList, key=lambda x: x.x)[len(_graph.nodesList) - 1].x# = canvasWidth (prend le maximum x des noeuds du graph )
    maxY = sorted(_graph.nodesList, key=lambda x: x.y)[len(_graph.nodesList) - 1].y# = canvasHeight (prend le maximum y des noeuds du graph )
    
    for node in _graph.nodesList :
        #Représentation des noeuds
        xC = (node.x*canvasWidth)/maxX
        yC = (node.y*canvasHeight)/maxY
        canvas.create_rectangle(xC-4, yC-4, xC+4, yC+4, fill=color)
        
        offsetX = -10
        offsetY = 0
        if yC/canvasHeight > .85: offsetY = -10
        elif  yC/canvasHeight < .15: offsetY = 10
        if xC/canvasWidth < .15: offsetX = 10
        #Représentation des identifiants des noeuds
        canvas.create_text(xC+offsetX, yC+offsetY, text=node.id, fill="#FFFFFF")
            
def updateCostTour(cost):
    global cost_text
    cost_text.set("Best tour found : " + str(cost))
    
def updateProgressBar(a, text):
    progressbar['value'] = a
    progressbar_text.set(text)
    root.update()

def refreshDraw(*args):
    canvas.delete("all")
    if client.displayEdges.get() and len(graphList) > 0 : drawEdges(graphList[0], graphList[0].spawningTree, client.edgesColorCode[1])
    if client.displayNodes.get() and len(graphList) > 0 : drawNodes(graphList[0], client.nodesColorCode[1])
    representationNodesColor.config(bg=client.nodesColorCode[1], fg=client.nodesColorCode[1])
    representationEdgesColor.config(bg=client.edgesColorCode[1], fg=client.edgesColorCode[1])
    
def loadBenchmark():
    currentTime = time()
    
    #Reset
    cost_text.set(" ")
    canvas.delete("all")
    graphList.clear()
    
    
    if not readfile(listbox.curselection()[0]): return #S'il n'est pas possible de lire le fichier TSP, c'est qu'il n'est pas compatible.
    loadFullGraphArcs(graphList[0])
    graphList[0].spawningTree = Kruskal(graphList[0])#Chargement de l'arbre couvrant de poids minimal
    #drawGraphe(graphList[0])
    #drawBenchmark()
    if client.displayEdges.get() : drawEdges(graphList[0], graphList[0].spawningTree, client.edgesColorCode[1])
    if client.displayNodes.get() : drawNodes(graphList[0], client.nodesColorCode[1])
    perfectMatching(graphList[0])
    drawEdges(graphList[0], graphList[0].perfectMatchingEdges, '#FF0000')
    eulerianCycle = eulerian(graphList[0])
    drawEdges(graphList[0], eulerianCycle, '#00FF00')
    print("Temps de chargement total : " + str(time() - currentTime) + ".")
    
def perfectMatching(_graph):
    oddDegreeNodes = []
    matchingEdges = []
    nodes = _graph.nodesList.copy()
    
    while len(nodes) > 0 :#Calcul des degrés impair. On regarde les occurences d'un noeud dans tous les arcs. Si le nombre d'occurences est impair, on ajoute à la liste des noeud impairs le noeud.
        currentNode = nodes.pop(0)
        count = 0
        for edge in _graph.spawningTree :
            if edge.startNode == currentNode or edge.finishNode == currentNode : count = count + 1
            #print(edge.startNode.id, edge.finishNode.id)
        if count % 2 != 0 : oddDegreeNodes.append(currentNode)
    
    while len(oddDegreeNodes) > 0 :#Pour chaque noeud de degré impair, on va chercher un autre noeud de degré impair libre le plus proche
        currentNode = oddDegreeNodes.pop(0)
        cost = INFINITE
        tempNode = NULL
        for oddNode in oddDegreeNodes :
            tempCost = math.sqrt(math.pow(currentNode.x - oddNode.x, 2) + math.pow(currentNode.y - oddNode.y, 2))
            if tempCost < cost:
                cost = tempCost
                tempNode = oddNode
        matchingEdges.append(Edge(currentNode, tempNode, cost))
        oddDegreeNodes.remove(tempNode)
    
    _graph.perfectMatchingEdges = matchingEdges

def getCycle(_goalNode, _tempEdges):
    cycle = []
    currentNode = _goalNode
    tempEdges = _tempEdges
    start = True
    
    while currentNode != _goalNode or start == True:
        start = False
        matchingEdges = [x for x in tempEdges if (x.startNode == currentNode or x.finishNode == currentNode)]
        
        print(_goalNode.id)
        for edge in matchingEdges:
            print(str(edge.startNode.id), str(edge.finishNode.id))
        
        selected = matchingEdges[0]
        if selected.startNode != currentNode :#Condition simplement pour conserver un ordre pratique de départ et d'arrivé
            currentNode = selected.startNode
            selected.startNode, selected.finishNode =  selected.finishNode, selected.startNode
        else : 
            currentNode = selected.finishNode
        
        #print("Choosen edge : " + str(selected.startNode.id), str(selected.finishNode.id))
        cycle.append(selected)
        tempEdges.remove(selected)
            
    if len(tempEdges) > 0 :
        for edge in cycle :
            
            #print(str(edge.startNode.id), str(edge.finishNode.id))
            node = edge.startNode
            
            neighborsEdges = [x for x in tempEdges if (x.startNode == node or x.finishNode == node)]
            #print(str(node.id), " : ", len(neighborsEdges))
            if(len(neighborsEdges) > 0) :
                
                #print(str(node.id), ", Nbr : ", len(neighborsEdges))
                #for neighborEdge in neighborsEdges:
                #    print(str(neighborEdge.startNode.id), str(neighborEdge.finishNode.id))
                    
                for neighborEdge in neighborsEdges:
                    
                    #print(str(node.id))
                    #print("index ", tempEdges.index(neighborEdge))
                    
                    #print("\n")
                    #for edge in cycle :
                    #    print(str(edge.startNode.id), str(edge.finishNode.id))
                        
                    #indexList = range(0,tempEdges.index(neighborEdge))
                    #part1 = [cycle[i] for i in indexList]
                    #for edge in part1 :
                    #    print("T, ", str(edge.startNode.id), str(edge.finishNode.id))
                    index = tempEdges.index(neighborEdge)
                    print("START : ", str(neighborEdge.finishNode.id))
                    [subCycle, tempEdges] = getCycle(neighborEdge.finishNode, tempEdges)
                    for edge in subCycle :
                        print("T, ", str(edge.startNode.id), str(edge.finishNode.id))
                    
                    cycle[index:index] = subCycle
                    #cycle = cycle.insert(index, part2)
                    print(cycle)
                    break
                
    return [cycle, tempEdges]
    
def eulerian(_graph):# Appliquer l'algorithme de Hierholzer
    eulerianGraph = []
    tempArcs = _graph.spawningTree.copy() + _graph.perfectMatchingEdges.copy()
    currentNode = _graph.nodesList[0]
    [eulerianGraph, tempArcs] = getCycle(currentNode, tempArcs)
    
    for edge in eulerianGraph:
        print(str(edge.startNode.id), str(edge.finishNode.id))
    return eulerianGraph

def hamiltonian(eulerianGraph):
    hamiltonien = pd.DataFrame(columns=["idS","idE","cost"])
    visitingOrder = []
    
    for i, row in eulerianGraph.iterrows():
        if row['idS'] in visitingOrder : continue
        visitingOrder.append(row['idS'])
    visitingOrder.append(visitingOrder[0])
    
    for i in range(len(visitingOrder)-1):
        row = allArcs.loc[((allArcs['idS'] == visitingOrder[i]) & (allArcs['idE'] == visitingOrder[i+1])) | ((allArcs['idE'] == visitingOrder[i]) & (allArcs['idS'] == visitingOrder[i+1]))]
        row = row.iloc[0]
        row = pd.DataFrame([[row['idS'],row['idE'],row['cost']]], columns=["idS","idE","cost"])
        hamiltonien = pd.concat([hamiltonien, row], axis=0, ignore_index=True)
    return hamiltonien
    
def resolveChristofides():
    global arcs
    currentTime = time()
    arcs = pd.concat([arcs, perfectMatching()], axis=0, ignore_index=True)    
    #drawArcs(arcs, '#FFFFFF') 

    eulerianGraph = eulerian()
    #print(eulerianGraph)
    #drawArcs(eulerianGraph, '#FFFFFF')
    
    hamiltonien = hamiltonian(eulerianGraph)
    #print(hamiltonian)
    #drawArcs(hamiltonien, '#FF0000')
    #print(eulerianGraph['idE'].value_counts())
    updateCostTour(round(hamiltonien['cost'].sum(),2))
    print("Temps de chargement : " + str(time() - currentTime) + ".")

filesList()

validate = tk.Button(root, text="Load", command=loadBenchmark).grid(column=0, row=3)
resolveChristofidesBtn = tk.Button(root, text="Resolve with Christofides", command=resolveChristofides).grid(column=2, row=2, pady=10)
drawNodesRadio = tk.Checkbutton(configuration, text="Display nodes", var=client.displayNodes, command=refreshDraw, bg="white").grid(column=0, row=0, pady=5)
drawEdgesRadio = tk.Checkbutton(configuration, text="Display edges", var=client.displayEdges, command=refreshDraw, bg="white").grid(column=0, row=1, pady=5)
edgesSizeScale = tk.Scale(configuration, orient='horizontal', var=client.edgeSize, command=refreshDraw, from_=0.5, to=10, resolution=0.25, tickinterval=4, length=100, label='Edge size', bg="white").grid(column=0, row=2, pady=5)

nodesColorBtn = tk.Button(configuration, text="Nodes color", command=lambda:[client.selectNodesColor(), refreshDraw()]).grid(column=0, row=3, sticky="w")
representationNodesColor = tk.Label(configuration, text="CCC", bg=client.nodesColorCode[1], fg=client.nodesColorCode[1], borderwidth=2, relief="solid")
representationNodesColor.grid(column=0, row=3, sticky="e", pady=5)

edgesColorBtn = tk.Button(configuration, text="Edges color", command=lambda:[client.selectEdgesColor(), refreshDraw()]).grid(column=0, row=4, sticky="w")
representationEdgesColor = tk.Label(configuration, text="CCC", bg=client.edgesColorCode[1], fg=client.edgesColorCode[1], borderwidth=2, relief="solid")
representationEdgesColor.grid(column=0, row=4, sticky="e", pady=5)

demoModeRadio = tk.Checkbutton(configuration, text="DEMO MODE", var=client.demoMode, command=refreshDraw, bg="white").grid(column=0, row=5, pady=5)

root.mainloop()


#Charger un fichier => N'afficher que les villes
#Cliquer sur Christofides => Afficher le graph complet ; Afficher l'arbre de poids minimal ; etc...
