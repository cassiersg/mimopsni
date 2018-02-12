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
Utilitary functions.
"""

import re

import networkx as nx
import matplotlib.pyplot as plt

def flatten(x):
    return (z for y in x for z in y)

def draw_graph(g, cut=tuple()):
    mapping = {node: node+g.nodes[node].get('op', '') for node in g}
    cut = [(mapping[src], mapping[end], e_id) for src, end, e_id in cut]
    g = nx.relabel_nodes(g, mapping)
    pos=nx.nx_agraph.graphviz_layout(g, prog='dot')
    n_colors = [n_color(g, n) for n in g]
    el = set(g.edges)
    nx.draw(
        g,
        pos,
        with_labels=True,
        arrows=True,
        edgelist=list(el - set(cut)),
        node_color=n_colors,
        node_size=600)
    if cut:
        nx.draw_networkx_edges(
            g,
            pos,
            edgelist=list(el & set(cut)),
            edge_color='r',
            arrows=True)

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

