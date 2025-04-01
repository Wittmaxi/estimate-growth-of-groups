import networkx as nx
import itertools
import numpy as np
from numpy import linalg as LA
import heapq

def blowup(graph):
    ret_graph = graph.copy()
    new_edges = []
    inverse_nodes = {}

    for node in list(ret_graph.nodes):
        inverse_node = f"-{node}"
        inverse_nodes[node] = inverse_node
        ret_graph.add_node(inverse_node) 
            
    for node1, node2 in ret_graph.edges:
        if node1 in inverse_nodes and node2 in inverse_nodes:
            inverse_node1 = inverse_nodes[node1]
            inverse_node2 = inverse_nodes[node2]
            new_edges.append((inverse_node1, inverse_node2))
            new_edges.append((inverse_node1, node2))
            new_edges.append((node1, inverse_node2))

    ret_graph.add_edges_from(new_edges)
    return ret_graph        

def unblowup(graph):
    ret_graph = graph.copy()
    for node in list(ret_graph.nodes):
        if node.startswith("-"):
            ret_graph.remove_node(node)
    
    return ret_graph

def calculate_graph_eigenvalue(graph):
    graph_copy = graph.copy()
    print (graph)
    graph_copy = blowup(graph_copy)
    eig = 0
    if graph_copy.size() != 0:
        eig = calculate_blowup_eigenvalue(graph_copy)
    return eig
    
def star(graph, node):
    graph_copy = graph.copy()
    if node not in graph_copy:
        raise ValueError("Node not in graph")

    neighbors = set(graph_copy.neighbors(node))

    nodes_to_remove = set(graph_copy.nodes) - neighbors
    graph_copy.remove_nodes_from(nodes_to_remove)
    return graph_copy


def calculate_mu1(graph):
    graph_copy = graph.copy()
    max_mu1 = 0
    for node in graph:
        subgraph = star(graph_copy, node)
        mu1 = calculate_graph_eigenvalue(subgraph)
        if max_mu1 < mu1:
            max_mu1 = mu1
    return max_mu1

def calculate_extensions(graph, subgraph):
    extensions = [0]
    for node in subgraph:
        extension_graph = star(graph, node)
        shared_nodes = set(subgraph.nodes) & set(extension_graph.nodes)
        extension_graph.remove_nodes_from(shared_nodes)
        print(extension_graph)
        print(extension_graph.size())
        print(extensions)
        if extension_graph.size() != 0:
            print("added extension")
            print ("loop 2, node: " + node)
            extensions.append(calculate_graph_eigenvalue(extension_graph))
    return np.array(extensions, dtype=np.float64)

def calculate_mu2(graph):
    graph_copy = graph.copy()
    max_mu2 = 0

    for node in graph:
        print("loop 1, node: " + node)
        subgraph = star(graph_copy, node)
        mu1 = calculate_graph_eigenvalue(subgraph)
        extensions = calculate_extensions(graph_copy, subgraph)
        print("extensions: " + str(extensions))
        bigex = heapq.nlargest(1, extensions)
        if (len(bigex) < 2):
            mu2 = 0
        else:
            mu2 = mu1 * bigex[0] * bigex[1]
        if max_mu2 < mu2:
            max_mu2 = mu2
    
    return max_mu2

# Probleme:
# ist s1 = s2 erlaubt?
# was, wenn es nur ein s1 gibt? Oder gar keins?

def calculate_blowup_eigenvalue(g):
    cliques = list(nx.find_cliques(g))

    all_cliques = []
    for clique in cliques:
        for r in range(1, len(clique) + 1):
            for subclique in itertools.combinations(clique, r):
                subclique_set = set(subclique)
                if not has_inverse_in_clique(subclique_set):
                    if frozenset(subclique_set) not in all_cliques:
                        all_cliques.append(frozenset(subclique_set))

    clique_index = {clique: idx for idx, clique in enumerate(all_cliques)}

    matrix = [[0] * len(all_cliques) for _ in range(len(all_cliques))]

    for alpha in all_cliques:
        for beta in all_cliques:
            if check_condition(set(alpha), set(beta), g):
                matrix[clique_index[alpha]][clique_index[beta]] = 1

    A = np.matrix(matrix)
    values, _ = LA.eig(A)
    largesteigenwert = np.argmax(values)
    if np.any(values == 0):
        print("not invertable")
    return values[largesteigenwert]
    
def has_inverse_in_clique(clique):
    for node in clique:
        if node.startswith("-"):
            uninverse_node = node[1:]
            if uninverse_node in clique:
                return True
        else:
            inverse_node = f"-{node}"
            if inverse_node in clique:
                return True
    return False

def check_condition(alpha, beta, g):
    for v in alpha:
        if v.startswith("-"):
            uninverse_v = v[1:]
            if uninverse_v in beta:
                return False
        else:
            inverse_v = f"-{v}"
            if inverse_v in beta:
                return False
            

    common_link = set(g.nodes())
    for node in alpha:
        common_link = common_link.intersection(set(g.neighbors(node)))

    if not common_link.isdisjoint(beta - alpha):
        return False
    return True