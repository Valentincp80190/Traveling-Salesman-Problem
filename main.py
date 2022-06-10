from asyncio.windows_events import INFINITE, NULL
import math
import random
from time import sleep, time
import tkinter as tk
from tkinter import HORIZONTAL, VERTICAL, Label, StringVar, ttk, colorchooser
import os
from os import walk
from client import Client
from edge import Edge
from g import G
from node import Node
from solution import Solution

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
cost_label = Label(root, textvariable=cost_text, bg="white").grid(column=2, columnspan=1, row=3)

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
graphList = []

client = Client(root)

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
    #Calcul du poids de tous les arcs pour avoir un graph complet
    nodesList = _graph.nodesList
    for startNode in nodesList :
        for finishNode in nodesList :
            if startNode == finishNode : continue
            cost = math.sqrt(math.pow(startNode.x - finishNode.x, 2) + math.pow(startNode.y - finishNode.y, 2))
            startNode.edgesList.append(Edge(startNode, finishNode, cost))
            
    print("Completed graph time : " + str(time() - currentTime) + ".")
    
def Kruskal(_graph): #Permet de générer un arbre couvrant minimal
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

def drawEdges(_graph, _edges, color, skip):
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
        
        #Ajout du mode démo
        if client.demoMode.get() == True and skip == False: 
            while client.isPause == True or (client.isNext == False and client.autoNext.get() == False):
                sleep(.1)
                #print("In pause...")
                root.update()
                
            if client.autoNext.get() == True :
                sleep(client.sleepTime.get())
                canvas.update()
                continue
            
            canvas.update()
            client.isNext = False

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

def refreshDraw(*args):
    canvas.delete("all")
    if client.displayNodes.get() and len(graphList) > 0 : drawNodes(graphList[0], client.nodesColorCode[1])
    if client.displayEdges.get() and len(graphList) > 0 : 
        if graphList[0].bestSolution != 0 : 
            drawEdges(graphList[0], graphList[0].bestSolution.hamiltonianCycleEdges, client.edgesColorCode[1], False)
        elif len(graphList[0].eulerianCycle) > 0 : 
            drawEdges(graphList[0], graphList[0].eulerianCycle, client.edgesColorCode[1], False)
        elif len(graphList[0].perfectMatchingEdges) > 0 :
            drawEdges(graphList[0], graphList[0].spawningTree, client.edgesColorCode[1], True)
            drawEdges(graphList[0], graphList[0].perfectMatchingEdges, "#FFFF00", False)
        else : drawEdges(graphList[0], graphList[0].spawningTree, client.edgesColorCode[1], False)
    if client.displayNodes.get() and len(graphList) > 0 : drawNodes(graphList[0], client.nodesColorCode[1])
    representationNodesColor.config(bg=client.nodesColorCode[1], fg=client.nodesColorCode[1])
    representationEdgesColor.config(bg=client.edgesColorCode[1], fg=client.edgesColorCode[1])

def drawSolution(solution):
    canvas.delete("all")
    
    if client.displayEdges.get() and len(graphList) > 0 : 
        maxX = sorted(solution.hamiltonianCycleNodes, key=lambda x: x.x)[len(solution.hamiltonianCycleNodes) - 1].x# = canvasWidth (prend le maximum x des noeuds du graph )
        maxY = sorted(solution.hamiltonianCycleNodes, key=lambda x: x.y)[len(solution.hamiltonianCycleNodes) - 1].y# = canvasHeight (prend le maximum y des noeuds du graph )
        
        #Représentation des arcs    
        #updateProgressBar(80, "Preparing to display graph arcs...")
        
        for edge in solution.hamiltonianCycleEdges :
            x1 = (edge.startNode.x*canvasWidth)/maxX
            y1 = (edge.startNode.y*canvasHeight)/maxY
            x2 = (edge.finishNode.x*canvasWidth)/maxX
            y2 = (edge.finishNode.y*canvasHeight)/maxY
            canvas.create_line(x1,y1,x2,y2, fill=client.edgesColorCode[1], width=client.edgeSize.get())
            
    if client.displayNodes.get() and len(graphList) > 0 : 
        for node in solution.hamiltonianCycleNodes :
            #Représentation des noeuds
            xC = (node.x*canvasWidth)/maxX
            yC = (node.y*canvasHeight)/maxY
            canvas.create_rectangle(xC-4, yC-4, xC+4, yC+4, fill=client.nodesColorCode[1])
            
            offsetX = -10
            offsetY = 0
            if yC/canvasHeight > .85: offsetY = -10
            elif  yC/canvasHeight < .15: offsetY = 10
            if xC/canvasWidth < .15: offsetX = 10
            #Représentation des identifiants des noeuds
            canvas.create_text(xC+offsetX, yC+offsetY, text=node.id, fill="#FFFFFF")
    canvas.update()
    
def loadBenchmark():
    currentTime = time()
    
    #Reset
    cost_text.set(" ")
    canvas.delete("all")
    graphList.clear()
    
    
    if not readfile(listbox.curselection()[0]): return #S'il n'est pas possible de lire le fichier TSP, c'est qu'il n'est pas compatible.
    loadFullGraphArcs(graphList[0])
    
    graphList[0].spawningTree = Kruskal(graphList[0])#Chargement de l'arbre couvrant de poids minimal
    refreshDraw(graphList[0])
    
    perfectMatching(graphList[0])
    refreshDraw(graphList[0])
    
    eulerian(graphList[0])
    hamiltonian(graphList[0])
    refreshDraw(graphList[0])
    
    two_opt(graphList[0])
    drawSolution(graphList[0].bestSolution)
    
    two_opt(graphList[0])
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
    
    #Ajouter une part d'aléatoire
    random.shuffle(oddDegreeNodes)
    
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

def getCycle(_graph, _goalNode, _tempEdges):
    cycle = []
    currentNode = _goalNode
    tempEdges = _tempEdges
    start = True
    
    while currentNode != _goalNode or start == True:
        start = False
        matchingEdges = [x for x in tempEdges if (x.startNode == currentNode or x.finishNode == currentNode)]
        
        selected = matchingEdges[0]
        if selected.startNode != currentNode :#Condition simplement pour conserver un ordre pratique de départ et d'arrivé
            currentNode = selected.startNode
            selected.startNode, selected.finishNode =  selected.finishNode, selected.startNode
        else : 
            currentNode = selected.finishNode
        cycle.append(selected)
        tempEdges.remove(selected)
    
    #if client.demoMode.get() == True :
    #    r = lambda: random.randint(0,255)
    #    #print('#%02X%02X%02X' % (r(),r(),r()))
    #    drawEdges(_graph, cycle, '#%02X%02X%02X' % (r(),r(),r()))
            
    if len(tempEdges) > 0 :#A la fin d'un cycle, on va voir s'il existe encore des arcs qui n'ayant pas encore été parcouru. 
        for edge in cycle :
            node = edge.startNode
            
            neighborsEdges = [x for x in tempEdges if (x.startNode == node or x.finishNode == node)]
            if(len(neighborsEdges) > 0) :
                for neighborEdge in neighborsEdges:
                    index = tempEdges.index(neighborEdge)
                    [subCycle, tempEdges] = getCycle(_graph, neighborEdge.finishNode, tempEdges)
                    
                    cycle[index:index] = subCycle
                    break
                
    return [cycle, tempEdges]
    
def eulerian(_graph):# Appliquer l'algorithme de Hierholzer
    eulerianGraph = []
    tempArcs = _graph.spawningTree.copy() + _graph.perfectMatchingEdges.copy()
    currentNode = _graph.nodesList[0]
    [eulerianGraph, tempArcs] = getCycle(_graph, currentNode, tempArcs)
    _graph.eulerianCycle = eulerianGraph

def hamiltonian(_graph):
    visitingNodeOrder = []
    edgesList = []
    
    for edge in _graph.eulerianCycle:
        if edge.startNode in visitingNodeOrder : continue
        visitingNodeOrder.append(edge.startNode)
    visitingNodeOrder.append(visitingNodeOrder[0])
    
    for i in range(len(visitingNodeOrder)-1):
        cost = math.sqrt(math.pow(visitingNodeOrder[i].x - visitingNodeOrder[i+1].x, 2) + math.pow(visitingNodeOrder[i].y - visitingNodeOrder[i+1].y, 2))
        edgesList.append(Edge(visitingNodeOrder[i], visitingNodeOrder[i+1], cost))
    
    cost = 0
    for edge in edgesList:
        cost = cost + edge.cost
        
    _graph.bestSolution = Solution(visitingNodeOrder, edgesList, cost)
    updateCostTour(cost)  

def two_opt(_graph): 
    s0 = _graph.bestSolution.hamiltonianCycleNodes
    print("best : ", str(_graph.bestSolution.cost))
    
    sn = s0
    bestFound = s0.copy()
    bestCost = _graph.bestSolution.cost
    cost = _graph.bestSolution.cost
    edges = []
    
    #for node in s0:
    #    print(str(node.id))
    
    improve = True
    while improve == True : 
        improve = False
        for i in range(len(s0) - 1) :
            for j in range(len(s0) - 1) :
                if i == j : continue
                
                sn = s0[:]
                sn.pop()
                sn[i], sn[j] = sn[j], sn[i]
                sn.append(sn[0])
                
                cost = 0
                for y in range(len(s0) - 1) :
                    cost = cost + math.sqrt(math.pow(sn[y].x - sn[y+1].x, 2) + math.pow(sn[y].y - sn[y+1].y, 2))
                    #print("cost from ", str(sn[y].id), " to ", str(sn[y+1].id), " =", cost)  
                
                if  cost < bestCost :
                    bestFound = sn[:]
                    bestCost = cost
                    improve = True
                    #print("trouvé mieux :", bestCost)
                    
                    if client.demoMode.get() == True :
                        tempEdges = []
                        
                        for i in range(len(bestFound) - 1) :
                            tempEdges.append(Edge(s0[i], s0[i+1], 0))
                            
                        solution = Solution(bestFound, tempEdges, 0)
                        drawSolution(solution)
                        sleep(client.sleepTime.get())
                        
        s0 = bestFound[:]
        
        #print("BEST found :")
        #for node in bestFound :
        #    print(str(node.id))
        #print(bestCost)
    
    for i in range(len(s0) - 1) :
        edges.append(Edge(s0[i], s0[i+1], 0))
        
    _graph.bestSolution = Solution(bestFound,edges,bestCost)
    updateCostTour(bestCost)
    #drawEdges(_graph, edges, "#0000FF")
    
filesList()

validate = tk.Button(root, text="Load", command=loadBenchmark).grid(column=0, row=3)
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
autoNextRadio = tk.Checkbutton(configuration, text="Auto next", var=client.autoNext, command=refreshDraw, bg="white").grid(column=0, row=6, pady=5)
edgesSizeScale = tk.Scale(configuration, orient='horizontal', var=client.sleepTime, from_=0.1, to=2, resolution=.1, tickinterval=.8, length=100, label='Time step (s)', bg="white").grid(column=0, row=7, pady=5)
pauseBtn = tk.Button(configuration, text="Pause", command=client.pause).grid(column=0, row=8, sticky="w")
nextBtn = tk.Button(configuration, text=" Next ", command=client.next).grid(column=0, row=8, sticky="e")


root.mainloop()


#Charger un fichier => N'afficher que les villes
