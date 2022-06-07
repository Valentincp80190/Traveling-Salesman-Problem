from asyncio.windows_events import INFINITE, NULL
import math
from time import time
import tkinter as tk
from tkinter import HORIZONTAL, VERTICAL, Label, StringVar, ttk
import os
from os import walk
from turtle import width
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
progressbar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=850).grid(column=0, columnspan=3, row=5)

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
        
client = Client()

class G():
    def __init__(self):
        self.nodesList = []
        self.edgesList = []
        self.spawningTree = []
        
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
    
def drawGraphe(_graph):
    currentTime = time()
    canvas.delete("all")
    
    maxX = sorted(_graph.nodesList, key=lambda x: x.x)[len(_graph.nodesList) - 1].x# = canvasWidth (prend le maximum x des noeuds du graph )
    maxY = sorted(_graph.nodesList, key=lambda x: x.y)[len(_graph.nodesList) - 1].y# = canvasHeight (prend le maximum y des noeuds du graph )
    
    #Représentation des arcs    
    #updateProgressBar(80, "Preparing to display graph arcs...")
    
    for node in _graph.nodesList :
        for edge in node.edgesList :
            x1 = (edge.startNode.x*canvasWidth)/maxX
            y1 = (edge.startNode.y*canvasHeight)/maxY
            x2 = (edge.finishNode.x*canvasWidth)/maxX
            y2 = (edge.finishNode.y*canvasHeight)/maxY
            canvas.create_line(x1,y1,x2,y2, fill="#FFFFFF")
    
    #updateProgressBar(90, "Preparing to display graph nodes...")
    for node in _graph.nodesList :
        #Représentation des noeuds
        xC = (node.x*canvasWidth)/maxX
        yC = (node.y*canvasHeight)/maxY
        canvas.create_rectangle(xC-4, yC-4, xC+4, yC+4, fill="#FF0000")
        
        offsetX = -10
        offsetY = 0
        if yC/canvasHeight > .85: offsetY = -10
        elif  yC/canvasHeight < .15: offsetY = 10
        if xC/canvasWidth < .15: offsetX = 10
        #Représentation des identifiants des noeuds
        canvas.create_text(xC+offsetX, yC+offsetY, text=node.id, fill="#FFFFFF")
        
    #updateProgressBar(100, "Loading complete !")
    print("Drawing time: " + str(time() - currentTime) + ".")
    #updateProgressBar(0, " ")
    
    
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

def drawNodes(_graph):
    maxX = sorted(_graph.nodesList, key=lambda x: x.x)[len(_graph.nodesList) - 1].x# = canvasWidth (prend le maximum x des noeuds du graph )
    maxY = sorted(_graph.nodesList, key=lambda x: x.y)[len(_graph.nodesList) - 1].y# = canvasHeight (prend le maximum y des noeuds du graph )
    
    for node in _graph.nodesList :
        #Représentation des noeuds
        xC = (node.x*canvasWidth)/maxX
        yC = (node.y*canvasHeight)/maxY
        canvas.create_rectangle(xC-4, yC-4, xC+4, yC+4, fill="#FF0000")
        
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

def refreshDraw():
    if client.displayEdges.get() : drawEdges(graphList[0], arcs, "#FF0000")
    if client.displayNodes.get() : drawNodes(graphList[0])
    
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
    if client.displayEdges.get() : drawEdges(graphList[0], graphList[0].spawningTree, "#FF0000")
    if client.displayNodes.get() : drawNodes(graphList[0])
    print("Temps de chargement total : " + str(time() - currentTime) + ".")
    
def perfectMatching():
    oddDegreeNodes = []
    #Neuds de degrés impair
    serieIdS = pd.Series(data=arcs["idS"])
    serieIdE = pd.Series(data=arcs["idE"])
    test = pd.concat([serieIdS, serieIdE])
    test = pd.Series(test.value_counts())
    for node, value in test.items():
        if (value)%2 != 0 : oddDegreeNodes.append(node)
    
    perfectMatching = pd.DataFrame(columns=['idS','idE','cost'])
    while len(oddDegreeNodes) > 0:
        node = oddDegreeNodes.pop(0)
        cost = INFINITE
        tempNode = NULL
        #A REFAIRE => Utiliser .min etc... de pandas
        for oddNode in oddDegreeNodes:    
            tempCost = math.sqrt(math.pow(nodes.iloc[node]["x"] - nodes.iloc[oddNode]["x"], 2) + math.pow(nodes.iloc[node]["y"] - nodes.iloc[oddNode]["y"], 2))
            
            if tempCost < cost: #Et qu'il n'existe pas de lien entre ces deux noeuds
                if len(arcs.loc[(arcs['idS'] == node) & (arcs['idE'] == oddNode)]) == 0 and len(arcs.loc[(arcs['idS'] == oddNode) & (arcs['idE'] == node)]) == 0:
                    cost = tempCost
                    tempNode = oddNode
        
        row = pd.DataFrame([[node,tempNode,cost]], columns=["idS","idE","cost"])
        oddDegreeNodes.remove(tempNode)
        perfectMatching = pd.concat([perfectMatching, row], axis=0, ignore_index=True)
    return perfectMatching

def getCycle(goalNode, tempArcs):
    cycle = pd.DataFrame(columns=["idS","idE","cost"])
    currentNode = goalNode
    start = True
    while currentNode != goalNode or start == True:
        start = False
        matchingArcs = tempArcs.loc[(tempArcs["idS"] == currentNode) | ((tempArcs["idE"] == currentNode))]
        
        selected = matchingArcs.iloc[0]
        
        if selected['idS'] != currentNode :#Condition simplement pour conserver un ordre pratique de départ et d'arrivé
            currentNode = selected['idS']
            row = pd.DataFrame([[selected['idE'],selected['idS'],selected['cost']]], columns=["idS","idE","cost"])
        else : 
            currentNode = selected['idE']
            row = pd.DataFrame([[selected['idS'],selected['idE'],selected['cost']]], columns=["idS","idE","cost"])
            
        cycle = pd.concat([cycle, row], axis=0, ignore_index=True)
        tempArcs.drop(matchingArcs.index[0], inplace=True)

    if len(tempArcs) > 0 :
        for i in range(len(cycle)):
            node = cycle.iloc[(len(cycle) - 1) - i]
            node = node['idS'] if node['idS'] != currentNode else node['idE']

            neighbors = tempArcs.loc[(tempArcs["idS"] == node) | ((tempArcs["idE"] == node))] 

            if len(neighbors) > 0:
                matchingArcs = neighbors
                [P2, tempArcs] = getCycle(node, tempArcs)
                
                index = len(cycle) - i
                P1 = cycle.head(index - 1)
                P3 = cycle.iloc[index-1::]
                c = pd.concat([P1, P2], axis=0, ignore_index=True)
                cycle = pd.concat([c, P3], axis=0, ignore_index=True)
                break
    return [cycle,tempArcs]
    
def eulerian():# Appliquer l'algorithme de Hierholzer
    eulerianGraph = pd.DataFrame(columns=["idS","idE","cost"])
    tempArcs = arcs
    currentNode = 0
    [eulerianGraph, tempArcs] = getCycle(currentNode, tempArcs)
    
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
validate = tk.Button(root, text="Load", command=loadBenchmark).grid(column=0, row=3, pady=10)
resolveChristofidesBtn = tk.Button(root, text="Resolve with Christofides", command=resolveChristofides).grid(column=2, row=2, pady=10)
drawNodesRadio = tk.Checkbutton(configuration, text="Display nodes", var=client.displayNodes, command=refreshDraw).grid(column=0, row=0)
drawEdgesRadio = tk.Checkbutton(configuration, text="Display edges", var=client.displayEdges).grid(column=0, row=1)
edgesSizeScale = tk.Scale(configuration, orient='horizontal', var=client.edgeSize, from_=0.5, to=10, resolution=0.25, tickinterval=4, length=100, label='Edge size').grid(column=0, row=2)
root.mainloop()


#Charger un fichier => N'afficher que les villes
#Cliquer sur Christofides => Afficher le graph complet ; Afficher l'arbre de poids minimal ; etc...
