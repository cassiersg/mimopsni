
import numpy as np
import networkx as nx
import scipy.optimize
import pulp
from matplotlib import pyplot as plt

nodes = list(range(15))
SNI_nodes = set([3, 8, 10, ]) # and 13

edges = [
    (0, 1), (1, 5), (1, 2), (2, 3), (3, 4), (4, 5), (4, 13), (5, 6), (6, 7),
    (6, 10), (7, 8), (8, 9), (9, 10), (9, 12), (10, 11), (11, 12), (12, 13),
    (13, 14),
]

gaes = nx.MultiDiGraph()
gaes.add_nodes_from(nodes)
gaes.add_edges_from(edges)
gaes.nodes.data()[0]['IN'] = True
gaes.nodes.data()[14]['OUT'] = True
for node_id, attrs in gaes.nodes.data():
    attrs['SNI'] = node_id in SNI_nodes

def cut_SNI(g):
    """Removes all successor edges of SNI gates"""
    for node in g.nodes:
        if g.nodes.data()[node]['SNI']:
            # there should be only zero or one out edge
            for e in list(g.out_edges(node, keys=True)):
                g.remove_edge(*e)

def flat_paths(g):
    paths = compute_paths(g)
    return {(src, dst): paths
            for src, p in paths.items()
            for dst, paths in p.items()
            }

def opt_setup(g):
    all_paths = flat_paths(g)
    n_paths = sum(len(p) for p in all_paths.values())
    edges = list(g.edges)
    e_ids = {e: i for i, e in enumerate(edges)}

    prob = pulp.LpProblem("edges", pulp.LpMinimize)
    ecuts = pulp.LpVariable.dicts("ecut", range(len(edges)), 0, 1, pulp.LpInteger)
    pcuts = pulp.LpVariable.dicts("pcut", range(n_paths), 0, 1, pulp.LpInteger) # int ?
    prob += sum(ecuts.values()), "number of cut edges"
    paths_sets_ids = {}
    for path_id, (path_set_id, path) in enumerate([(path_set_id, path) for path_set_id, ((src, dest), paths) in enumerate(all_paths.items()) for path in paths]):
        prob += pcuts[path_id] <= sum(ecuts[e_ids[edge]] for edge in path), "path is cut if at least one edge is cut " + str(path_id)
        paths_sets_ids.setdefault(path_set_id, []).append(path_id)
    for path_set_id, path_ids in paths_sets_ids.items():
        prob += sum(pcuts[path_id] for path_id in path_ids) >= len(path_ids) - 1, "Cut at least all but one paths " + str(path_set_id)
    # cut "pass-through" paths to get SNI
    for src in g.nodes:
        if g.nodes.data()[src].get('IN'):
            for dest in g.nodes:
                if g.nodes.data()[dest].get('OUT'):
                    for i, path in enumerate(all_paths.get((src, dest), [])):
                        prob += sum(ecuts[e_ids[edge]] for edge in path) >= 1, "pass-through path {} from {} to {}".format(i, src, dest)
    #prob.writeLP('aes.lp')
    print('Starting optimization...')
    prob.solve()
    print("Status:", pulp.LpStatus[prob.status])
    cut_edges = [edges[i] for i, e in ecuts.items() if pulp.value(e) == 1.0]
    print("Cut edges:", cut_edges)
    return cut_edges
    #print("Res:", [(edges[i], pulp.value(e)) for i, e in ecuts.items()])

def simplify_node(g, node):
    """If node has only:
    - one input, one output: remove node and merge incoming and outcoming edges
    - one input, no output: remove node and incident edge
    - no input, one output: remove node and incident edge
    - no input, no output: remove node
    Does not remove input and output nodes.
    Does not care about SNI (we assume cut_SNI has been called before).
    Returns True if the node was removed.
    """
    if g.nodes.data()[node].get('IN') or g.nodes.data()[node].get('OUT'):
        return False
    succ = list(g.out_edges(node, keys=True))
    pred = list(g.in_edges(node, keys=True))
    if len(succ) == 1 and len(pred) == 1:
        g.remove_node(node)
        g.add_edge(pred[0][0], succ[0][1])
        return True
    elif len(succ) <= 1 and len(pred) <= 1:
        g.remove_node(node)
        return True
    else:
        return False

def simplify_graph(g):
    simplifies = True
    while simplifies:
        simplifies = False
        try:
            for node in reversed(list(nx.topological_sort(g))):
                simplifies = simplifies or simplify_node(g, node)
        except nx.NetworkXUnfeasible:
            pos=nx.nx_agraph.graphviz_layout(g, prog='dot')
            nx.draw(g, pos, with_labels=True, arrows=True)
            break



def test_graph_NI(g):
    paths = compute_paths(g)
    return all(len(l) <= 1 for src, p in paths.items() for _, l in p.items())

def test_graph_SNI(g):
    paths = compute_paths(g)
    for src in g.nodes:
        if g.nodes.data()[src].get('IN'):
            for dest in g.nodes:
                if g.nodes.data()[dest].get('OUT'):
                    if paths.get(src, {}).get(dest, []):
                        return False
    return all(len(l) <= 1 for src, p in paths.items() for _, l in p.items())

def test():
    #cut_SNI(gaes)
    simplify_graph(gaes)
    import pprint
    #pprint.pprint(compute_paths(gaes))
    #import matplotlib.pyplot as plt
    #nx.draw(gaes, with_labels=True)
    #plt.show()
    print('NI:', test_graph_NI(gaes))
    print('SNI:', test_graph_SNI(gaes))
    print('edges', gaes.edges)
    #print('flat_paths', flat_paths(gaes))
    cut = opt_setup(gaes)
    show_cut_graph(gaes, cut)
    plt.show()

if __name__ == '__main__':
    test()
