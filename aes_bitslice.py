
import collections
import networkx as nx
import matplotlib.pyplot as plt
import copy
import graph
import paths_dag
import opt_sni
import utils

from utils import flatten, parse_string_graph, draw_graph, test_graph

from pprint import pprint

s = open('repr_aes_bitslice/non_lin.txt').read()
s_out = open('repr_aes_bitslice/lin_out.txt').read()
g = parse_string_graph(s)
g_out = parse_string_graph(s_out)
out_nodes = set(g_out.nodes)

for n in g.nodes:
    if g.in_degree(n) == 0:
        g.nodes[n]['IN'] = True
for n in out_nodes:
    if n in g.nodes:
        name = 'o' + n[1:]
        g.add_node(name)
        g.add_edge(n, name)
        g.nodes[name]['OUT'] = True

cnt = collections.Counter(len(list(g.successors(n))) for n in g.nodes)
print('cnt', cnt)

if 0:
    for n in set(g.nodes):
        succ = list(g.successors(n))
        if len(succ) > 1:
            for s in succ:
                g.remove_edge(n, s)
            name = n + 's'
            g.add_node(name)
            g.add_edge(n, name)
            for s in succ:
                g.add_edge(name, s)
else:
    split_c = []
    for n in set(g.nodes):
        succ = list(g.successors(n))
        if len(succ) > 1:
            for s in succ:
                g.remove_edge(n, s)
            l = []
            for i in range(len(succ)):
                name = n + 's' + str(i)
                l.append(name)
                g.add_node(name)
                g.add_edge(n, name)
                for s in succ:
                    g.add_edge(name, s)
            split_c.append(l)
    print('baseline cut', sum(len(x)*(len(x)-1) for x in split_c))


cut_edges = opt_sni.opt_sni(g, split_c, max_seconds=20)
g2 = utils.remove_edges_cut(g, cut_edges)

print('Cut is NI', paths_dag.is_graph_NI(g2))
print('Cut is SNI', paths_dag.is_graph_SNI(g2))

draw_graph(g, cut_edges)
plt.show()

g3 = utils.simplify_graph(g2, preserve_IO=False)
cut_edges = [x for x in cut_edges if x in g3.edges]
draw_graph(g3, cut_edges)
plt.show()

