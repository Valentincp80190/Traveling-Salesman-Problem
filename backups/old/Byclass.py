from asyncio.windows_events import INFINITE, NULL
import math
from time import time
import tkinter as tk
from tkinter import HORIZONTAL, VERTICAL, Label, StringVar, ttk
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
progressbar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=850)
progressbar.grid(column=0, columnspan=3, row=5)

canvasHeight = 600
canvasWidth = 700
canvas = tk.Canvas(root, bg="#202020", height=canvasHeight, width=canvasWidth)
canvas.grid(column=2, row=1)

script_dir = os.path.dirname(__file__) # Récupérer le chemin relatif au script
rel_path = "benchmarks"
abs_file_path = os.path.join(script_dir, rel_path) #Trouve le chemin absolu du dossier benchmarks

filenames = []
#nodes = pd.DataFrame(columns=["x","y","root"])
nodes = np.empty((0,3), np.float64)
arcs = np.empty((0,3), np.float64)
allArcs = arcs


graphList = []

class G():
    def __init__(self):
        self.nodeList = []
        
    def addNode(self, _node):
        self.nodeList.append(_node)
    
class Edge():
    def __init__(self, _startNode, _finishNode, _cost):
        self.startNode = _startNode
        self.finishNode = _finishNode
        self.cost = _cost
        
    def getCost(self):
        return self.cost
        
class Node():
    def __init__(self, _x, _y):
        self.x = _x 
        self.y = _y
        self.root = self
        self.edgeList = []

def filesList():
    global filenames
    filenames = next(walk(abs_file_path), (None, None, []))[2] #Parcours les fichiers de haut en bas dans un dossier
    filenames = [ file for file in filenames if file.endswith(".tsp") ] #Exclu les mauvaises extensions

    for filename in filenames: #Inject dans la liste à afficher les noms sans leur extensions
        listbox.insert(tk.END, filename[:filename.index('.')])

def readfile(benchmark):
    global nodes, graphList
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
                graphList[0].addNode(Node(float(line[1]), float(line[2])))
            except IndexError:
                break
        i = i + 1
    file.close
    print("Loading file time : " + str(time() - currentTime) + ".")
    return True
    
def loadFullGraphArcs():
    global arcs, allArcs
    currentTime = time()
    #updateProgressBar(30, "Creation of graph arcs...")  
    i=0
    #Calcul du poids de tous les arcs pour avoir un graph complet
    nodeList = graphList[0].nodeList
    for startNode in nodeList :
        for finishNode in nodeList :
            if startNode == finishNode : continue
            #if finishNode in nodeList.edgeList and startNode in nodeList.edgeList : continue
            cost = math.sqrt(math.pow(startNode.x - finishNode.x, 2) + math.pow(startNode.x - finishNode.y, 2))
            startNode.edgeList.append(Edge(startNode, finishNode, cost))
    
    #edgeCount = 0
    #for node in nodeList :
    #    edgeCount = edgeCount + len(node.edgeList)
    #print(edgeCount)
    print("Completed graph time : " + str(time() - currentTime) + ".")
    
def drawGraphe(_graphe):
    currentTime = time()
    canvas.delete("all")
    
    maxX = sorted(_graphe.nodeList, key=lambda x: x.x)[len(_graphe.nodeList) - 1].x# = canvasWidth (prend le maximum x des noeuds du graph )
    maxY = sorted(_graphe.nodeList, key=lambda x: x.y)[len(_graphe.nodeList) - 1].y# = canvasHeight (prend le maximum y des noeuds du graph )
    
    #Représentation des arcs    
    #updateProgressBar(80, "Preparing to display graph arcs...")
    
    for node in _graphe.nodeList :
        for edge in node.edgeList :
            x1 = (edge.startNode.x*canvasWidth)/maxX
            y1 = (edge.startNode.y*canvasHeight)/maxY
            x2 = (edge.finishNode.x*canvasWidth)/maxX
            y2 = (edge.finishNode.y*canvasHeight)/maxY
            canvas.create_line(x1,y1,x2,y2, fill="#FFFFFF")
    
    #updateProgressBar(90, "Preparing to display graph nodes...")
 
    for node in _graphe.nodeList :
        #Représentation des noeuds
        xC = (node.x*canvasWidth)/maxX
        yC = (node.y*canvasHeight)/maxY
        canvas.create_rectangle(xC-4, yC-4, xC+4, yC+4, fill="#FF0000")
        
    #updateProgressBar(100, "Loading complete !")
    print("Drawing time: " + str(time() - currentTime) + ".")
    #updateProgressBar(0, " ")
    
    
def Kruskal(): #Permet de générer un arbre couvrant minimal
    global arcs, nodes
    updateProgressBar(60, "Minimum spanning tree generation...")
    arcs = arcs.sort_values(by=['cost'])
    arcsKruskal = pd.DataFrame(columns=["idS","idE","cost"])
    
    for i, row in arcs.iterrows():
        if nodes.loc[row['idS']]['root'] == nodes.loc[row['idE']]['root'] : continue
        
        #Union
        rootIdS = nodes.loc[row['idS']]['root']
        rootIdE = nodes.loc[row['idE']]['root']
        nodes.loc[nodes['root'] == rootIdE, ['root']] = rootIdS
        
        row = pd.DataFrame([[row['idS'],row['idE'],row['cost']]], columns=["idS","idE","cost"])
        arcsKruskal = pd.concat([arcsKruskal, row], axis=0, ignore_index=True)
    arcs = arcsKruskal
    
def updateCostTour(cost):
    global cost_text
    cost_text.set("Best tour found : " + str(cost))
    
def updateProgressBar(a, text):
    progressbar['value'] = a
    progressbar_text.set(text)
    root.update()

def drawArcs(arcs, color):#A RETIRER CAR UTILISE QUE POUR LE COUPLAGE
    maxX = nodes["x"].max() # = canvasWidth
    maxY = nodes["y"].max() # = canvasHeight
    
    for i, rowA in arcs.iterrows():
        cS = nodes.iloc[rowA['idS']]
        xCS = (cS['x']*canvasWidth)/maxX
        yCS = (cS['y']*canvasHeight)/maxY
        
        cE = nodes.iloc[rowA['idE']]
        xCE = (cE['x']*canvasWidth)/maxX
        yCE = (cE['y']*canvasHeight)/maxY
        
        canvas.create_line(xCS,yCS,xCE,yCE, fill=color)
    
def loadBenchmark():
    global nodes, arcs
    #/////////////////RESET/////////////////
    cost_text.set(" ")
    canvas.delete("all")
    nodes = np.empty((0,3), np.float64)
    arcs = np.empty((0,3), np.float64)
    #///////////////END-RESET///////////////
    currentTime = time()
    
    if not readfile(listbox.curselection()[0]): return #S'il est impossible de lire le fichier TSP, c'est qu'il n'est pas compatible.
    loadFullGraphArcs()
    drawGraphe(graphList[0])
    #Kruskal() #Chargement de l'arbre couvrant minimal
    #drawBenchmark()
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
    drawArcs(hamiltonien, '#FF0000')
    #print(eulerianGraph['idE'].value_counts())
    updateCostTour(round(hamiltonien['cost'].sum(),2))
    print("Temps de chargement : " + str(time() - currentTime) + ".")
    
filesList()
validate = tk.Button(root, text="Load", command=loadBenchmark).grid(column=0, row=3, pady=10)
resolveChristofidesBtn = tk.Button(root, text="Resolve with Christofides", command=resolveChristofides).grid(column=2, row=2, pady=10)
root.mainloop()


#Charger un fichier => N'afficher que les villes
#Cliquer sur Christofides => Afficher le graph complet ; Afficher l'arbre de poids minimal ; etc...
