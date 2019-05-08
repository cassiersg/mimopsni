#! /usr/bin/python3

# Copyright 2018 Gaëtan Cassiers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Optimize number of refreshes in bitslice implementation of lightweight block
cipher.

Usage: python lw_opt.py <CIPHER>

Ciphers:
fantomas/f2.txt
present.txt
noekeon.txt
"""

import sys
import logging
logging.basicConfig(level=logging.INFO)

import networkx as nx
import matplotlib.pyplot as plt

import paths_dag
import opt_sni
import parse
import graph_tools

from utils import draw_graph

# like formatted but removes NOT operations
s = open(sys.argv[1]).read()
g = parse.parse(s, tag_output_fn=lambda g, n: n.startswith('y'))

draw_graph(g)
plt.show()

split_c_d = graph_tools.add_split_nodes(g)
split_c = list(split_c_d.values())
print('baseline cut', sum(len(x)*(len(x)-1) for x in split_c))

draw_graph(g)
plt.show()

cut_edges = opt_sni.opt_sni(g, split_c, max_seconds=32*3600*10)
g2 = graph_tools.without_edges(g, cut_edges)

print('Cut is NI', paths_dag.is_graph_NI(g2))
print('Cut is SNI', paths_dag.is_graph_SNI(g2))

draw_graph(g, cut_edges)
plt.show()

g3 = graph_tools.simplified(g2, preserve_IO=False)
cut_edges2 = [x for x in cut_edges if x in g3.edges]
draw_graph(g3, cut_edges2)
plt.show()

g4, ce = graph_tools.without_unncessary_splits(g, cut_edges, split_c_d)
draw_graph(g4, [x for x in cut_edges if x in g4.edges])
plt.show()
draw_graph(g, cut_edges)

