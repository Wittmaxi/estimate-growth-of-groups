import random
import numpy as np
from plot import *
from isjoin import *
from display_matrix import *
from tqdm import tqdm


def powerset(s):
    result = [[]]
    for elem in s:
        result.extend([x + [elem] for x in result])
    return result

def is_clique(graph, nodes):
    return all(graph[u][v] for i, u in enumerate(nodes) for v in nodes[i + 1:])

def find_cliques(graph):
    n = len(graph)
    nodes = list(range(n))
    max_cliques = []
    for subset in powerset(nodes):
        if is_clique(graph, subset):
            if not any(set(subset) < set(c) for c in max_cliques):
                max_cliques = [c for c in max_cliques if not set(c) < set(subset)]
                max_cliques.append(subset)
    return max_cliques

def link(graph, v):
    return {u for u, connected in enumerate(graph[v]) if connected}

def clique_move(graph, alpha, beta):
    # Gemeinsamer Link aller Knoten in alpha
    common_link = set(range(len(graph)))
    for v in alpha:
        common_link &= link(graph, v)
    # Neue Knoten in beta (die nicht in alpha waren)
    new_nodes = set(beta) - set(alpha)
    # Bedingung: Kein neuer Knoten liegt im gemeinsamen Link
    return len(new_nodes & common_link) == 0

def build_good_matrix(graph, cliques):
    n = len(cliques)
    matrix = [[0]*n for _ in range(n)]
    for i, alpha in enumerate(cliques):
        for j, beta in enumerate(cliques):
            if clique_move(graph, alpha, beta):
                matrix[i][j] = 1
    return matrix


def spectral_radius(matrix) -> float:
    matrix = np.array(matrix)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Die Eingabe muss eine quadratische 2D-Matrix sein.")

    eigenwerte = np.linalg.eigvals(matrix)
    return np.max(np.abs(eigenwerte))

def generate_random_graph(n, p):
    graph = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p and i != j:
                graph[i][j] = graph[j][i] = 1
    return graph

def find_all_cliques(graph):
    n = len(graph)
    nodes = list(range(n))
    all_cliques = []
    for subset in powerset(nodes):
        if len(subset) >= 1 and is_clique(graph, subset):
            all_cliques.append(subset)
    return all_cliques

def convert_to_nx_graph(graph):
    arr = np.array(graph)
    G = nx.from_numpy_array(arr)
    return G


def meet_condition(g1, g2):
    if (not g1 or not g2):
        print(g1)
        return False

    # try: # condition: g1 is cyclical
    #     nx.find_cycle(convert_to_nx_graph(g1))
    #     nx.find_cycle(convert_to_nx_graph(g2))
    # except nx.NetworkXNoCycle:
    #     return False

    g1 = convert_to_nx_graph(g1)
    g2 = convert_to_nx_graph(g2)
    # g1_connected = nx.is_connected(g1)
    # g2_connected = nx.is_connected(g2)
    # if(not g1_connected or not g2_connected):
    #     return False

    g1join = is_join(g1) 
    g2join = is_join(g2)

    if(g1join or g2join):
        return False
    
    return True


def main():
    count = 0
    num_graphs_per_update = 1000
    while True:
        count += 1
        random_integer = random.randint(1, 15)
        random_increase = random.randint(2, 3)
        g1 = generate_random_graph(random_integer + random_increase, random.random())  #Fixed the graph size to 6
        g2 = generate_random_graph(random_integer, random.random())

        cliques1 = find_all_cliques(g1)
        cliques2 = find_all_cliques(g2)

        if len(cliques1) > len(cliques2) and meet_condition(g1, g2):
            matrix1 = build_good_matrix(g1, cliques1)
            matrix2 = build_good_matrix(g2, cliques2)
            rho1 = spectral_radius(matrix1)
            rho2 = spectral_radius(matrix2)
            print(f"Graph 1: {len(cliques1)} Cliques, {random_integer + random_increase} nodes , Spektralradius = {rho1:.4f}")
            print(f"Graph 2: {len(cliques2)} Cliques, {random_integer} nodes Spektralradius = {rho2:.4f}")
            
            graph1_nx = convert_to_nx_graph(g1)  # Convert to NetworkX graph for plotting
            graph2_nx = convert_to_nx_graph(g2)

            display_results(np.array(matrix1), np.array(matrix2), graph1_nx, graph2_nx)

            if rho1 >= rho2:
                print("graph good")
            else:
                plot_two_adjacency_matrices_diff_size(np.array(g1), np.array(g2), layout_k=4)
                print(g1)
                print(g2)
                print(matrix1)
                print(matrix2)
                print("COUNTEREXAMPLE: Spektralradius ist nicht monoton.")
                exit()


if __name__ == "__main__":
    main()
