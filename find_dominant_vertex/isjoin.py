import networkx as nx

def is_join(G: nx.Graph) -> bool:
    """
    Prüft, ob der Graph G ein Join zweier nicht-leerer Teilgraphen ist,
    basierend auf der Zerlegung des Komplementärgraphen.

    Ein Graph G ist Join, wenn der Komplementärgraph von G nicht zusammenhängend ist
    und mindestens zwei Komponenten hat, die zusammen alle Knoten von G abdecken.

    Parameter:
    -----------
    G : nx.Graph
        Ein ungerichteter Graph.

    Rückgabe:
    ----------
    bool
        True, wenn G ein Join ist, sonst False.
    """

    n = G.number_of_nodes()
    if n < 2:
        # Mindestens zwei Knoten nötig
        return False

    # Komplementärgraph erzeugen
    G_comp = nx.complement(G)

    # Komponenten im Komplementärgraphen finden
    components = list(nx.connected_components(G_comp))

    if len(components) < 2:
        # Weniger als zwei Komponenten: Komplementärgraph zusammenhängend -> kein Join
        return False

    # Prüfe, ob keine Komponente leer ist und die Komponenten zusammen alle Knoten abdecken
    total_nodes = set()
    for comp in components:
        if len(comp) == 0:
            return False
        total_nodes.update(comp)

    # Sicherheitshalber prüfen, ob alle Knoten in Komponenten enthalten sind
    if total_nodes != set(G.nodes):
        return False

    # Mindestens zwei nicht-leere Komponenten, die alle Knoten abdecken -> Join
    return True

