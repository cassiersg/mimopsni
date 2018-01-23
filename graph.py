
import networkx as nx
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

def test():
    #cut_SNI(gaes)
    simplify_graph(gaes)
    import pprint
    #nx.draw(gaes, with_labels=True)
    #plt.show()
    print('NI:', test_graph_NI(gaes))
    print('SNI:', test_graph_SNI(gaes))
    print('edges', gaes.edges)
    cut = opt_setup(gaes)
    show_cut_graph(gaes, cut)
    plt.show()

if __name__ == '__main__':
    test()
