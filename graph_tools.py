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

"""Utilities for other modules"""

import copy
import re
import networkx as nx

def _simplify_node(g, node, preserve_IO=True):
    """If node has only:
    - one input, one output: remove node and merge incoming and outcoming edges
    - one input, no output: remove node and incident edge
    - no input, one output: remove node and incident edge
    - no input, no output: remove node
    Does not remove input and output nodes is perserve_IO is True.
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

def simplified(g, preserve_IO=True):
    """Graph without 'useless' nodes.

    A node is useless if its (number of inputs, number of outputs) is
    (1, 1), (1, 0), (0, 1) or (0, 0). Incident edges are also removed
    except in the case (1, 1) where they are merged.
    Input and output nodes are kept is perserver_IO is True.
    """
    g = copy.deepcopy(g)
    simplifies = True
    while simplifies:
        simplifies = False
        for node in reversed(list(nx.topological_sort(g))):
            simplifies = simplifies or _simplify_node(g, node, preserve_IO)
    return g

def without_edges(g, e):
    """Same as nx.remove_edges_from but does not modify original graph."""
    g = copy.deepcopy(g)
    g.remove_edges_from(e)
    return g

def add_split_nodes(g):
    split_n = dict()
    for n in list(g.nodes):
        succ = list(g.successors(n))
        if len(succ) > 1:
            # we need to split
            # remove output edges
            for s in succ:
                g.remove_edge(n, s)
            l = [] # list of split nodes for n
            # add split nodes and connect them
            for i in range(len(succ)):
                name = n + 's' + str(i)
                l.append(name)
                g.add_node(name)
                g.add_edge(n, name)
                for s in succ:
                    g.add_edge(name, s)
            split_n[n] = l
    return split_n

def remove_exceeding_split_edges(g, cut_edges, split_c_d):
    """Generates a graph without unncessary split edges.

    * graph g
    * cut_edges edges cut by algo
    * split_c_d dict {node: [associated split nodes]}
    """
    g = copy.deepcopy(g)
    g2 = without_edges(g, cut_edges)
    for n, sg in split_c_d.items():
        sg = list(sg)
        for dest in list(g.successors(sg[0])):
            if all((s, dest, 0) in cut_edges for s in sg):
                for s in sg[1:]:
                    g.remove_edge(s, dest)
            else:
                for s in sg:
                    if (s, dest, 0) in cut_edges:
                        g.remove_edge(s, dest)
    return g, list(set(cut_edges) & set(g.edges))

def without_unncessary_splits(g, cut_edges, split_c_d):
    """Generates a graph without unncessary split nodes.

    * graph g
    * cut_edges edges cut by algo
    * split_c_d dict {node: [associated split nodes]}
    """
    g, cut_edges = remove_exceeding_split_edges(g, cut_edges, split_c_d)
    new_cut_edges = []
    for n, sg in split_c_d.items():
        for s in sg:
            if g.out_degree(s) == 0:
                g.remove_node(s)
            elif g.out_degree(s) == 1:
                n2 = next(g.successors(s))
                if (n, s, 0) in cut_edges and (s, n2, 0) in cut_edges:
                    raise ValueError(n, s, n2)
                if (s, n2, 0) in cut_edges or (n, s, 0) in cut_edges:
                    new_cut_edges.append((n, n2, 0))
                g.add_edge(n, n2)
                g.remove_node(s)
    return g, list(set(cut_edges) & set(g.edges)) + new_cut_edges

