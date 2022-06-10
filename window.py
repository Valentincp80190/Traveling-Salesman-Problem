import tkinter as tk
from tkinter import HORIZONTAL, VERTICAL, Label, StringVar, Toplevel, ttk
import matplotlib.pyplot as plt

class Window():
    def __init__(self):
        self.root = tk.Tk()
        self.style = ttk.Style(self.root)
        self.style.theme_use('winnative')

        self.root['bg']='white'
        self.root.title("Traveling Salesman Problem")
        self.root.resizable(0, 0)

        tk.Label(self.root, text="Benchmarks", bg="white").grid(column=0, row=0)
        tk.Label(self.root, text="Simulation", bg="white").grid(column=2, row=0)
        tk.Label(self.root, text="Configuration", bg="white").grid(column=3, row=0)

        self.listbox = tk.Listbox(self.root)
        self.scrollbarV = tk.Scrollbar(self.root, orient=VERTICAL)
        self.scrollbarH = tk.Scrollbar(self.root, orient=HORIZONTAL)
        self.scrollbarV.grid(column=1, row=1, sticky="ns")
        self.scrollbarH.grid(column=0, row=2, sticky="ew")
        self.listbox.grid(column=0, row=1, sticky="nsew") # north + east [...]
        self.listbox.config(yscrollcommand=self.scrollbarV.set)
        self.listbox.config(xscrollcommand=self.scrollbarH.set)
        self.scrollbarV.config(command=self.listbox.yview)
        self.scrollbarH.config(command=self.listbox.xview)

        self.cost_text = StringVar()
        self.cost_label = Label(self.root, textvariable=self.cost_text, bg="white").grid(column=2, columnspan=1, row=3)

        self.canvasHeight = 600
        self.canvasWidth = 700
        self.canvas = tk.Canvas(self.root, bg="#202020", height=self.canvasHeight, width=self.canvasWidth)
        self.canvas.grid(column=2, row=1)
        
        self.configuration = tk.Frame(self.root, bg="#FFFFFF")
        self.configuration.grid(column=3, row=1, sticky="nes")
        
    def showTrace(self, _serie):
        plt.plot(_serie)
        plt.title("Evolution of cost")
        plt.ylabel('Cost tour')
        plt.show()
        