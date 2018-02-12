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
Find optimal set of refresh for implementation of AES inversion in GF(256).
"""

import itertools as it

import networkx as nx
from matplotlib import pyplot as plt

import paths_dag
import utils

# See figure 6 in "Randomness Complexity of Private Circuits for Multiplication, Belaid et al., Eurocrypt 2016"
nodes = ['i', 'is', 'a9', 'a9s', 'a7', 'a7s', 'a6', 'a6s', 'a4', 'a3', 'a2', 'a1', 'o']
edges = [
    ('i', 'is'), ('is', 'a7'), ('is', 'a9'),
    ('a9', 'a9s'), ('a9s', 'a7'), ('a9s', 'a1'),
    ('a7', 'a7s'), ('a7s', 'a4'), ('a7s', 'a6'),
    ('a6', 'a6s'), ('a6s', 'a2'), ('a6s', 'a4'),
    ('a4', 'a3'), ('a3', 'a2'),
    ('a2', 'a1'), ('a1', 'o'),
]

def test_ni_cut(cut, kind='SNI'):
    """True if the SBox with edges cut is SNI.

    cut: list of 16 booleans, True => SNI element
    kind: 'SNI' or 'NI'
    """
    edges_remaining = [e for e, c in zip(edges, cut) if not c]
    g= nx.MultiDiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges_remaining)
    g.nodes.data()['i']['IN'] = True
    g.nodes.data()['o']['OUT'] = True
    if kind == 'NI':
        return paths_dag.is_graph_NI(g)
    elif kind == 'SNI':
        return paths_dag.is_graph_SNI(g)
    else:
        raise ValueError(kind)

def binary_combinations(k, n):
    for idxes in it.combinations(list(range(n)), k):
        res = n*[False]
        for i in idxes:
            res[i] = True
        yield res

def find_efficient_ni(threshold=3, kind='SNI'):
    """List all cuts that give NI/SNI (depending on kind) with
    at most threshold SNI elements.
    """
    return [comb for comb in binary_combinations(threshold, len(edges))
            if test_ni_cut(comb, kind)]

def wrap_result_lin(x):
    """Remove redundancies (ie. edges before and after 2^j power gadgets)"""
    x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15 = x
    return (x0, x1, x2+x3, x4, x5, x6, x7, x8+x9, x10, x11, x12+x13, x14, x15)

def test():
    g = nx.MultiDiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    utils.draw_graph(g)
    plt.show()

if __name__ == '__main__':
    #test()
    from pprint import pprint
    pprint(set(wrap_result_lin(list(map(int, x))) for x in find_efficient_ni(3, 'SNI')))
