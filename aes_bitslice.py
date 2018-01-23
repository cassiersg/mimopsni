
import logging
logging.basicConfig(level=logging.DEBUG)

import networkx as nx
import matplotlib.pyplot as plt

import paths_dag
import opt_sni
import parse
import graph_tools

from utils import draw_graph

s = open('repr_aes_bitslice/non_lin.txt').read()
s_out = open('repr_aes_bitslice/lin_out.txt').read()
g_out = parse.parse_string_graph(s_out)
out_nodes = set(g_out.nodes)
g = parse.parse(s, tag_output_fn=lambda g, n: n in out_nodes)

split_c_d = graph_tools.add_split_nodes(g)
split_c = list(split_c_d.values())
print('baseline cut', sum(len(x)*(len(x)-1) for x in split_c))

cut_edges = opt_sni.opt_sni(g, split_c, max_seconds=20)
g2 = graph_tools.without_edges(g, cut_edges)

print('Cut is NI', paths_dag.is_graph_NI(g2))
print('Cut is SNI', paths_dag.is_graph_SNI(g2))

#draw_graph(g, cut_edges)
#plt.show()

#g3 = graph_tools.simplified(g2, preserve_IO=False)
#cut_edges2 = [x for x in cut_edges if x in g3.edges]
#draw_graph(g3, cut_edges2)
#plt.show()

g4 = graph_tools.without_unncessary_splits(g, cut_edges, split_c_d)
draw_graph(g4, [x for x in cut_edges if x in g4.edges])
plt.show()

