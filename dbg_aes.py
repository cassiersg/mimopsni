
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
#print('desc', desc)
#print('asc', asc)
#print('sg', desc & asc)
g2 = g.subgraph(sg).copy()
g2.add_edge('t26', 't32')
#split_c2 = [x for x in split_c if any(y in g2.nodes for y in x)]
split_c2 = [['t23s0', 't23s1']]
print('split_c', split_c2)
#
#all_paths = paths_dag.compute_paths(g2)
#p1 = paths_dag.expand_compressed_paths(g2, all_paths)
#print('n_total_paths', paths_dag.n_paths(p1))
#p2 = paths_dag.compute_paths_old(g2)
#assert paths_dag.expanded_path_to_comparable(p1) == paths_dag.expanded_path_to_comparable(p2)
#assert 0

cut_edges = opt_sni.opt_sni(g2, split_c2)
draw_graph(g2, cut_edges)
#draw_graph(g)
plt.show()

#g = utils.remove_edges_cut(g, cut_edges)
#g = utils.simplify_graph(g)
#print('start opt setup')
#draw_graph(g)

#pos=nx.nx_agraph.graphviz_layout(gaes, prog='dot')
#nx.draw(gaes, pos, with_labels=True, arrows=True)

#assert not in_nodes & out_nodes
#assert not list(nx.simple_cycles(gaes))

#for n in in_nodes: gaes.nodes[n]['IN'] = True
#for n in out_nodes: gaes.nodes[n]['OUT'] = True

#g2 = copy.deepcopy(gaes)
#graph.simplify_graph(g2)

#pos=nx.nx_agraph.graphviz_layout(g2, prog='dot')
#nx.draw(g2, pos, with_labels=True, arrows=True)

#cut = graph.opt_setup(g2)
#paths = graph.compute_paths2(g2)
#n_paths = sum(len(p) for x in paths for p in x)
#print('n_paths', n_paths)
#graph.show_cut_graph(g2, cut)
#plt.show()

