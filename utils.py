
import copy
import re
import networkx as nx
import matplotlib.pyplot as plt

def parse_assign(assign):
    dst, expr = assign.split('=')
    expr_n = expr.replace('*', '+')
    src1, src2 = expr_n.split('+')
    op = expr[expr_n.find('+')]
    return (dst, op, (src1, src2))

def flatten(x):
    return (z for y in x for z in y)

def test_graph(g):
    assert not any(g.nodes[n]['IN'] and g.nodes[n]['OUT'] for n in g.nodes)
    assert not list(nx.simple_cycles(g))

def draw_graph(g, cut=tuple()):
    #g, cut = remove_cut_split_edges(g, cut)
    #g, cut = simplify_graph_display(g, cut)
    mapping = {node: node+g.nodes[node].get('op', '') for node in g}
    cut = [(mapping[src], mapping[end], e_id) for src, end, e_id in cut]
    g = nx.relabel_nodes(g, mapping)
    pos=nx.nx_agraph.graphviz_layout(g, prog='dot')
    n_colors = [n_color(g, n) for n in g]
    #el = filter_draw_edges(g, cut)
    el = list(g.edges)
    nx.draw(g, pos, with_labels=True, arrows=True, edgelist=el, node_color=n_colors, node_size=600)
    #nx.draw_networkx_edges(g, pos, edgelist=el, arrows=True)
    if cut:
        print('cut drawn', list(set(el) & set(cut)))
        nx.draw_networkx_edges(g, pos, edgelist=list(set(el) & set(cut)), edge_color='r', arrows=True)

def remove_cut_split_edges(g, cut=tuple()):
    g = copy.deepcopy(g)
    ea = set(g.edges)
    unwanted = set(e for e in g.edges if is_split_node(e[0])) & set(cut)
    for e in unwanted:
        assert e in ea
        g.remove_edge(*e)
    return g, list(set(g.edges) & set(cut))

def filter_draw_edges(g, cut):
    if cut is None:
        return list(g.edges)
    else:
        unwanted = set(e for e in g.edges if re.search('s[0-9]?$', e[0])) & set(cut)
        print(unwanted)
        return list(set(g.edges) - unwanted)

def simplify_graph_display(g, cut):
    g = copy.deepcopy(g)
    cut = set(cut)
    for n in list(g.nodes):
        succ = list(g.successors(n))
        if not succ:
            if not g.nodes[n].get('OUT'):
                g.remove_node(n)
        elif len(succ) == 1 and is_split_node(n):
            assert len(list(g.predecessors(n))) == 1
            p = list(g.predecessors(n))[0]
            s = succ[0]
            g.add_edge(p, s)
            g.remove_node(n)
            if (p, n, 0) in cut or (n, s, 0) in cut:
                cut.discard((p, n, 0))
                cut.discard((n, s, 0))
                cut.add((p, s, 0))
    return g, list(cut)

def simplify_node(g, node, preserve_IO=True):
    """If node has only:
    - one input, one output: remove node and merge incoming and outcoming edges
    - one input, no output: remove node and incident edge
    - no input, one output: remove node and incident edge
    - no input, no output: remove node
    Does not remove input and output nodes.
    Does not care about SNI (we assume cut_SNI has been called before).
    Returns True if the node was removed.
    """
    if preserve_IO and (g.nodes.data()[node].get('IN') or g.nodes.data()[node].get('OUT')):
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

def simplify_graph(g, preserve_IO=True):
    g = copy.deepcopy(g)
    simplifies = True
    while simplifies:
        for node in reversed(list(nx.topological_sort(g))):
            simplifies = simplify_node(g, node, preserve_IO)
    return g

def remove_edges_cut(g, edges):
    g = copy.deepcopy(g)
    for e in edges:
        g.remove_edge(*e)
    return g

def is_split_node(n):
        return bool(re.search('s[0-9]?$', n))

def n_color(g, n):
    if g.nodes[n].get('IN'):
        return 'xkcd:pale green'
    elif g.nodes[n].get('OUT'):
        return 'xkcd:beige'
    elif re.search('s[0-9]?$', n): #n.endswith('s'):
        return 'xkcd:light gray'
    else:
        return 'xkcd:light blue'

def draw_graph_cut(g, cut):
    draw_graph(g, cut)
    plt.show()

def parse_string_graph(s):
    l = [parse_assign(x) for x in s.splitlines()]
    nodes = set(flatten((dst, *srcs) for dst, op, srcs in l))
    edges = list(flatten(((src1, dst), (src2, dst)) for dst, op, (src1, src2) in l))
    g = nx.MultiDiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    for dst, op, _ in l:
        g.nodes[dst]['op'] = op
    return g

