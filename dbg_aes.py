
import collections

import logging
logging.basicConfig(level=logging.DEBUG)

import networkx as nx
import matplotlib.pyplot as plt

import graph
import paths_dag
import opt_sni
import utils
import parse
import graph_tools

from utils import draw_graph


s = open('repr_aes_bitslice/non_lin.txt').read()
s_out = open('repr_aes_bitslice/lin_out.txt').read()
g_out = parse.parse_string_graph(s_out)
out_nodes = set(g_out.nodes)
g = parse.parse(s, tag_output_fn=lambda g, n: n in out_nodes)

split_c = graph_tools.add_split_nodes(g)
split_c = list(split_c.values())
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

