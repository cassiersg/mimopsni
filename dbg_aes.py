
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

desc = set(['t23'] + list(nx.algorithms.dag.descendants(g, 't23')))
asc = set(['t32'] + list(nx.algorithms.dag.ancestors(g, 't32')))
sg = asc & desc - {'t26s0', 't26s1', 't31', 't23s2'}
g2 = g.subgraph(sg).copy()
g2.add_edge('t26', 't32')
split_c2 = [['t23s0', 't23s1']]
print('split_c', split_c2)

cut_edges = opt_sni.opt_sni(g2, split_c2)
draw_graph(g2, cut_edges)
plt.show()

