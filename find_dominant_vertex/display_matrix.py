import tkinter as tk
import numpy as np
import random
import networkx as nx
from plot import * # Assuming this file contains plot_two_adjacency_matrices_diff_size
from isjoin import * # Assuming this file contains is_join

def sort_matrix(matrix):
    """Sorts the matrix rows in ascending order based on the sum of each row."""
    row_sums = np.sum(matrix, axis=1)
    sorted_indices = np.argsort(row_sums)  # Indices that would sort the sums
    sorted_matrix = matrix[sorted_indices]  #Sort rows of the matrix by the indices
    return sorted_matrix



def pad_matrix(smaller_matrix, larger_size):
    """Pads a smaller matrix with zeros to match a larger size."""
    rows_to_add = larger_size[0] - smaller_matrix.shape[0]
    cols_to_add = larger_size[1] - smaller_matrix.shape[1]
    padded_matrix = np.pad(smaller_matrix, ((0, rows_to_add), (0, cols_to_add)), mode='constant')
    return padded_matrix



def display_results(matrix1, matrix2, graph1, graph2):
    """Displays adjacency matrices and graphs in a single figure."""

    fig, axes = plt.subplots(3, 2, figsize=(12, 15))

    # Original Matrix 1
    axes[0, 0].imshow(matrix1, cmap='binary')
    axes[0, 0].set_title("Adjacency Matrix 1 (Original)")
    axes[0, 0].set_xticks(np.arange(matrix1.shape[1]))
    axes[0, 0].set_yticks(np.arange(matrix1.shape[0]))

    # Sorted Matrix 1
    sorted_matrix1 = sort_matrix(matrix1)
    axes[1, 0].imshow(sorted_matrix1, cmap='binary')
    axes[1, 0].set_title("Adjacency Matrix 1 (Sorted)")
    axes[1, 0].set_xticks(np.arange(sorted_matrix1.shape[1]))
    axes[1, 0].set_yticks(np.arange(sorted_matrix1.shape[0]))

    # Graph 1
    pos1 = nx.spring_layout(graph1)
    nx.draw(graph1, pos1, with_labels=True, node_size=500, ax=axes[2, 0])
    axes[2, 0].set_title("Graph 1")

    # Original Matrix 2
    axes[0, 1].imshow(matrix2, cmap='binary')
    axes[0, 1].set_title("Adjacency Matrix 2 (Original)")
    axes[0, 1].set_xticks(np.arange(matrix2.shape[1]))
    axes[0, 1].set_yticks(np.arange(matrix2.shape[0]))

    # Pad and Sort Matrix 2
    padded_matrix2 = pad_matrix(matrix2, matrix1.shape) #Pad to match size of matrix1
    sorted_matrix2 = sort_matrix(padded_matrix2)
    axes[1, 1].imshow(sorted_matrix2, cmap='binary')
    axes[1, 1].set_title("Adjacency Matrix 2 (Padded and Sorted)")
    axes[1, 1].set_xticks(np.arange(sorted_matrix2.shape[1]))
    axes[1, 1].set_yticks(np.arange(sorted_matrix2.shape[0]))

    # Graph 2
    pos2 = nx.spring_layout(graph2)
    nx.draw(graph2, pos2, with_labels=True, node_size=500, ax=axes[2, 1])
    axes[2, 1].set_title("Graph 2")

    plt.tight_layout()
    plt.show()
