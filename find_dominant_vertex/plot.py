import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_two_adjacency_matrices_diff_size(adj1: np.ndarray, adj2: np.ndarray, labels1=None, labels2=None, layout_k=1.0):
    """
    Visualisiert zwei Graphen aus zwei Adjazenzmatrizen unterschiedlicher Größe,
    mit größerem Abstand zwischen Knoten durch Anpassung des spring_layout-Parameters `k`.

    Parameter:
    -----------
    adj1, adj2 : np.ndarray
        Zwei quadratische Adjazenzmatrizen.
    labels1, labels2 : dict (optional)
        Knotenlabels.
    layout_k : float
        Parameter für den Abstand im spring_layout (Standard 1.0).
        Größere Werte erhöhen den Abstand zwischen Knoten.
    """
    n1 = adj1.shape[0]
    n2 = adj2.shape[0]

    G = nx.DiGraph()
    nodes1 = range(n1)
    nodes2 = range(n1, n1 + n2)
    G.add_nodes_from(nodes1)
    G.add_nodes_from(nodes2)

    if labels1 is None:
        labels1 = {i: str(i) for i in nodes1}
    else:
        labels1 = {i: labels1.get(i, str(i)) for i in nodes1}

    if labels2 is None:
        labels2 = {i + n1: str(i + n1) for i in range(n2)}
    else:
        labels2 = {i + n1: labels2.get(i, str(i + n1)) for i in range(n2)}

    for i in range(n1):
        for j in range(n1):
            if adj1[i, j] != 0:
                G.add_edge(i, j, color='red', weight=adj1[i, j])

    for i in range(n2):
        for j in range(n2):
            if adj2[i, j] != 0:
                G.add_edge(i + n1, j + n1, color='blue', weight=adj2[i, j])

    # Hier der wichtige Parameter: k für Federlänge im Layout
    pos = nx.spring_layout(G, k=layout_k, iterations=100)

    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    weights = []
    for u, v in edges:
        w = G[u][v]['weight']
        weights.append(sum(w) if isinstance(w, tuple) else w)
    max_w = max(weights) if weights else 1
    widths = [3 * (w / max_w) for w in weights]

    nx.draw_networkx_nodes(G, pos, nodelist=nodes1, node_color='lightcoral')
    nx.draw_networkx_nodes(G, pos, nodelist=nodes2, node_color='lightblue')

    labels = {**labels1, **labels2}
    nx.draw_networkx_labels(G, pos, labels)

    nx.draw_networkx_edges(G, pos, edge_color=colors, width=widths, arrowsize=20)

    red_patch = mpatches.Patch(color='lightcoral', label='Graph 1 (Knoten)')
    blue_patch = mpatches.Patch(color='lightblue', label='Graph 2 (Knoten)')
    red_edge = mpatches.Patch(color='red', label='Graph 1 (Kanten)')
    blue_edge = mpatches.Patch(color='blue', label='Graph 2 (Kanten)')

    plt.legend(handles=[red_patch, blue_patch, red_edge, blue_edge])
    plt.axis('off')
    plt.show()

