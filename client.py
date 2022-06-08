import tkinter as tk
from tkinter import colorchooser

class Client():
    def __init__(self, _root):
        root = _root
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