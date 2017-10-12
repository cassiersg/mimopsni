
import numpy as np
import networkx as nx
import scipy.optimize

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

def compute_paths(g):
    paths_nodes = {}
    for node in reversed(list(nx.topological_sort(g))):
        paths = {}
        for _, succ, e_id in g.out_edges(node, keys=True):
            for dest, sub_paths in paths_nodes[succ].items():
                for sub_path in sub_paths:
                    paths.setdefault(dest, list()).append([(node, succ, e_id)]+sub_path)
            paths.setdefault(succ, list()).append([(node, succ, e_id)])
        paths_nodes[node] = paths
    return paths_nodes

def flat_paths(g):
    paths = compute_paths(g)
    return {(src, dst): paths
            for src, p in paths.items()
            for dst, paths in p.items()
            }

def opt_setup(g):
    all_paths = flat_paths(g)
    n_paths = sum(len(p) for p in all_paths.values())
    edges = g.edges
    e_ids = {e: i for i, e in enumerate(edges)}
    A_ub11 = np.zeros((len(all_paths), n_paths))
    A_ub12 = np.zeros((len(all_paths), len(edges)))
    b_ub1 = np.zeros((len(all_paths),))

    A_ub21 = np.zeros((n_paths, n_paths)) # identity matrix
    A_ub22 = np.zeros((n_paths, len(edges)))
    b_ub2 = np.zeros((n_paths,)) # zero vector
    print('n_paths', n_paths)
    print('len(edges)', len(edges))
    print('len(all_apths)', len(all_paths))

    for path_id, (path_set_id, path) in enumerate([(path_set_id, path) for path_set_id, ((src, dest), paths) in enumerate(all_paths.items()) for path in paths]):
        A_ub11[path_set_id,path_id] = -1
        A_ub21[path_id, path_id] = 1
        for edge in path:
            e_id = e_ids[edge]
            A_ub22[path_id,e_id] = -1
    for path_set_id, ((src, dest), paths) in enumerate(all_paths.items()):
        b_ub1[path_set_id] = -(len(paths) - 1)

    A_ub = np.concatenate((np.concatenate((A_ub11, A_ub12), axis=1), np.concatenate((A_ub21, A_ub22), axis=1)), axis=0)
    print('b_ub1', b_ub1)
    print('b_ub2', b_ub2)
    b_ub = np.concatenate((b_ub1, b_ub2), axis=0)
    c = np.concatenate((np.zeros((n_paths,)), np.ones((len(edges),))), axis=0)
    bounds = (0, 1)
    opt = scipy.optimize.linprog(c, A_ub, b_ub, bounds=bounds)
    print(repr(opt))
    print(opt.x)



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
        for node in reversed(list(nx.topological_sort(g))):
            simplifies = simplifies or simplify_node(g, node)

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
    pprint.pprint(compute_paths(gaes))
    #import matplotlib.pyplot as plt
    #nx.draw(gaes, with_labels=True)
    #plt.show()
    print('NI:', test_graph_NI(gaes))
    print('SNI:', test_graph_SNI(gaes))
    print('edges', gaes.edges)
    print('flat_paths', flat_paths(gaes))
    opt_setup(gaes)

if __name__ == '__main__':
    test()
