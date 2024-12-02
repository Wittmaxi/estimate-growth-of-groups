import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import itertools
import numpy as np
from numpy import linalg as LA
from dask.array import argmax

class GraphInputGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Input Interface")

        # Initialize graph structure
        self.graph = nx.Graph()

        # Node input
        tk.Label(root, text="Node:").grid(row=0, column=0, padx=5, pady=5)
        self.node_entry = tk.Entry(root)
        self.node_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Add Node", command=self.add_node).grid(row=0, column=2, padx=5, pady=5)

        # Edge input
        tk.Label(root, text="Edge (Node1, Node2):").grid(row=1, column=0, padx=5, pady=5)
        self.edge_node1_entry = tk.Entry(root, width=10)
        self.edge_node1_entry.grid(row=1, column=1, padx=5, pady=5)
        self.edge_node2_entry = tk.Entry(root, width=10)
        self.edge_node2_entry.grid(row=1, column=2, padx=5, pady=5)
        tk.Button(root, text="Add Edge", command=self.add_edge).grid(row=1, column=3, padx=5, pady=5)

        # Graph visualization canvas
        self.graph_canvas_frame = tk.Frame(root)
        self.graph_canvas_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        
        # Calculate button
        tk.Button(root, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=4, pady=10)
        
        tk.Button(root, text="two point blow-up", command=self.blowup).grid(row=4, column=0, columnspan=4, pady=10)
        
        tk.Button(root, text="undo two point blow-up", command=self.unblowup).grid(row=5, column=0, columnspan=4, pady=10)
        
        tk.Button(root, text="do the line", command=self.line).grid(row=6, column=0, columnspan=4, pady=10)

    def line(self):
        self.add_node(string = str(0))
        for i in range(1, 10):
            self.add_node(string = str(i))
            self.add_edge(str(i), str(i-1))
            self.blowup()
            print("CALCULATING FOR " + str(i) + " NODES")
            self.calculate()
            self.unblowup()

    def add_node(self, string=None):
        if string == None:
            node = self.node_entry.get().strip()
        else:
            node = string
        if node:
            if node not in self.graph:
                self.graph.add_node(node)
                self.update_graph_display()
                self.node_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", f"Node '{node}' already exists.")
        else:
            messagebox.showerror("Error", "Node cannot be empty.")              

    def blowup(self):
        new_edges = []
        inverse_nodes = {}
    
        # Add inverse nodes and edges to their corresponding original nodes
        for node in list(self.graph.nodes):
            inverse_node = f"-{node}"
            inverse_nodes[node] = inverse_node  # Store inverse node for later reference
            self.graph.add_node(inverse_node)  # Add inverse node to the graph    
            new_edges.append((node, inverse_node))  # Connect node to its inverse
    
        # Add connections between inverses of connected nodes
        for node1, node2 in self.graph.edges:
            if node1 in inverse_nodes and node2 in inverse_nodes:
                inverse_node1 = inverse_nodes[node1]
                inverse_node2 = inverse_nodes[node2]
                new_edges.append((inverse_node1, inverse_node2))  # Connect inverses
    
        # Add all new edges to the graph
        self.graph.add_edges_from(new_edges)
    
        # Update the graph display
        self.update_graph_display()
        
    def unblowup(self):
        for node in list(self.graph.nodes):
            if node.startswith("-"):
                self.graph.remove_node(node)
        
        self.update_graph_display()

    def add_edge(self, node1=None, node2=None):
        if node1 == None:
            node1 = self.edge_node1_entry.get().strip()
        if node2 == None:
            node2 = self.edge_node2_entry.get().strip()
        if node1 and node2:
            if node1 in self.graph and node2 in self.graph:
                if not self.graph.has_edge(node1, node2):
                    self.graph.add_edge(node1, node2)
                    self.update_graph_display()
                    self.edge_node1_entry.delete(0, tk.END)
                    self.edge_node2_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", f"Edge between '{node1}' and '{node2}' already exists.")
            else:
                messagebox.showerror("Error", "Both nodes must exist to create an edge.")
        else:
            messagebox.showerror("Error", "Both nodes must be specified.")

    def update_graph_display(self):
        # Remove the previous graph canvas
        for widget in self.graph_canvas_frame.winfo_children():
            widget.destroy()

        # Create new figure and canvas for the updated graph
        fig, ax = plt.subplots(figsize=(6, 6))
        nx.draw(self.graph, with_labels=True, ax=ax, node_color='lightblue', font_weight='bold', node_size=500)
        
        # Embed the plot into the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def calculate(self):
        cliques = list(nx.find_cliques(self.graph))
    
        # Generate all valid subcliques without inverse/uninverse conflicts
        all_cliques = []
        for clique in cliques:
            for r in range(1, len(clique) + 1):  # Start at r = 1 to exclude empty cliques
                for subclique in itertools.combinations(clique, r):
                    subclique_set = set(subclique)
                    if not self.has_inverse_in_clique(subclique_set):
                        if frozenset(subclique_set) not in all_cliques:  # Avoid duplicates
                            all_cliques.append(frozenset(subclique_set))
    
        # Map cliques to indices
        clique_index = {clique: idx for idx, clique in enumerate(all_cliques)}
    
        # Initialize the adjacency matrix
        matrix = [[0] * len(all_cliques) for _ in range(len(all_cliques))]
    
        # Fill the matrix
        for alpha in all_cliques:
            for beta in all_cliques:
                if self.check_condition(set(alpha), set(beta)):
                    matrix[clique_index[alpha]][clique_index[beta]] = 1
    
        # Debugging: Print the number of cliques and verify matrix size
#        print(f"Number of valid cliques: {len(all_cliques)}")
#        print(f"Matrix size: {len(matrix)}x{len(matrix)}")
    
        # Prepare the output: Create a string for matrix display with clique labels
        matrix_str = "   " + "\t".join([str(sorted(clique)) for clique in all_cliques]) + "\n"
        for i, row in enumerate(matrix):
            matrix_str += str(sorted(all_cliques[i])) + "\t" + "\t".join(map(str, row)) + "\n"
    
        # Display the matrix in a message box
        # print("Clique Matrix", f"Matrix of Cliques:\n{matrix_str}")

        A = np.matrix(matrix)
        values, _ = LA.eig(A)
        largesteigenwert = np.argmax(values)
        print(values[largesteigenwert])

    def has_inverse_in_clique(self, clique):
        for node in clique:
            if node.startswith("-"):
                # If the node is an inverse, check if its "uninverse" is in the clique
                uninverse_node = node[1:]  # Remove the leading "-"
                if uninverse_node in clique:
                    return True
            else:
                # If the node is not an inverse, check if its inverse is in the clique
                inverse_node = f"-{node}"
                if inverse_node in clique:
                    return True
        return False

    def check_condition(self, alpha, beta):
        for v in alpha:
            if v.startswith("-"):
                # If v is an inverse node, its "uninverse" must not be in beta
                uninverse_v = v[1:]  # Remove the leading "-"
                if uninverse_v in beta:
                    return False
            else:
                # If v is a regular node, its inverse must not be in beta
                inverse_v = f"-{v}"
                if inverse_v in beta:
                    return False
                

        common_link = set(self.graph.nodes())
        for node in alpha:
            common_link = common_link.intersection(set(self.graph.neighbors(node)))

        if not common_link.isdisjoint(beta - alpha):  # If there is an intersection
            return False
        return True
        


# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphInputGUI(root)
    root.mainloop()
