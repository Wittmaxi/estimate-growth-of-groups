import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import itertools
from numpy import linalg as LA
from dask.array import argmax
from tkinter import filedialog
import pickle
from logic import *

class GraphInputGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Input Interface")
        self.graph = nx.Graph()
        self.star_graph = nx.Graph()

        tk.Label(root, text="Node:").grid(row=0, column=0, padx=5, pady=5)
        self.node_entry = tk.Entry(root)
        self.node_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Add Node", command=self.add_node).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(root, text="Edge (Node1, Node2):").grid(row=1, column=0, padx=5, pady=5)
        self.edge_node1_entry = tk.Entry(root, width=10)
        self.edge_node1_entry.grid(row=1, column=1, padx=5, pady=5)
        self.edge_node2_entry = tk.Entry(root, width=10)
        self.edge_node2_entry.grid(row=1, column=2, padx=5, pady=5)
        tk.Button(root, text="Add Edge", command=self.add_edge).grid(row=1, column=3, padx=5, pady=5)

        self.graph_canvas_frame = tk.Frame(root)
        self.graph_canvas_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        self.star_canvas_frame = tk.Frame(root)
        self.star_canvas_frame.grid(row=2, column=3,  columnspan=3)


        self.eigenwert_label = tk.Label(root, text="No eigenvalue calculated yet")
        self.eigenwert_label.grid(row=3, columnspan=5)
        
        tk.Button(root, text="Calculate", command=self.calculate_main_eigenvalue).grid(row=4, column=0)
        tk.Button(root, text="two point blow-up", command=self.do_blowup).grid(row=4, column=1)
        tk.Button(root, text="undo two point blow-up", command=self.do_unblowup).grid(row=4, column=2)
        self.load_button = tk.Button(root, text="Load Graph", command=self.load_graph).grid(row=5, column=0)
        self.save_button = tk.Button(root, text="Save Graph", command=self.save_graph).grid(row=5, column=1)
        self.clear_button = tk.Button(root, text="Clear Graph", command=self.clear_graph).grid(row=5, column=2)
        self.star_entry = tk.Entry(root)
        self.star_entry.grid(row=6,column=0)
        self.star_button = tk.Button(root, text="Get Star", command=self.reduce_to_star).grid(row=6, column=1)
        self.star_to_graph_button = tk.Button(root, text="promote star to graph", command=self.star_to_graph).grid(row=6, column=2)
        self.star_label = tk.Label(root, text="no Star calculated yet").grid(row=7, columnspan=5)

    def star_to_graph(self):
        self.graph = self.star_graph
        self.update_graph_display(self.graph_canvas_frame, self.graph)

    def reduce_to_star(self):
        self.star_graph = star(self.graph, self.star_entry.get().strip())
        self.update_graph_display(self.star_canvas_frame, self.star_graph)

    def do_blowup(self):
        self.graph = blowup(self.graph)
        self.update_graph_display(self.graph_canvas_frame, self.graph)

    def do_unblowup(self):
        self.graph = unblowup(self.graph)
        self.update_graph_display(self.graph_canvas_frame, self.graph)

    def clear_graph(self):
        self.graph.clear()
        self.update_graph_display(self.graph_canvas_frame, self.graph)

    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "wb") as f:
                pickle.dump(self.graph, f)
    
    def load_graph(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "rb") as f:
                self.graph = pickle.load(f)
        self.update_graph_display(self.graph_canvas_frame, self.graph)

    def add_node(self, string=None):
        if string == None:
            node = self.node_entry.get().strip()
        else:
            node = string
        if node:
            if node not in self.graph:
                self.graph.add_node(node)
                self.update_graph_display(self.graph_canvas_frame, self.graph)
                self.node_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", f"Node '{node}' already exists.")
        else:
            messagebox.showerror("Error", "Node cannot be empty.")              

    def add_edge(self, node1=None, node2=None):
        if node1 == None:
            node1 = self.edge_node1_entry.get().strip()
        if node2 == None:
            node2 = self.edge_node2_entry.get().strip()
        if node1 and node2:
            if node1 in self.graph and node2 in self.graph:
                if not self.graph.has_edge(node1, node2):
                    self.graph.add_edge(node1, node2)
                    self.update_graph_display(self.graph_canvas_frame, self.graph)
                    self.edge_node1_entry.delete(0, tk.END)
                    self.edge_node2_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", f"Edge between '{node1}' and '{node2}' already exists.")
            else:
                messagebox.showerror("Error", "Both nodes must exist to create an edge.")
        else:
            messagebox.showerror("Error", "Both nodes must be specified.")

    def update_graph_display(self, ui_canvas, graph):
        for widget in ui_canvas.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(4, 4))
        nx.draw(graph, with_labels=True, ax=ax, node_color='lightblue', font_weight='bold', node_size=100)
        
        canvas = FigureCanvasTkAgg(fig, master=ui_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def calculate_main_eigenvalue(self):
        eig = calculate_graph_eigenvalue(self.graph)
        mu1 = calculate_mu1(self.graph)
        mu2 = calculate_mu2(self.graph)
        self.eigenwert_label.config(text="λ = " + str(eig) + ", μ1 = " + str(mu1) + ", μ2 = " + str(mu2))
   
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphInputGUI(root)
    root.mainloop()
