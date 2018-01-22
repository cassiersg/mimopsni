
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

#desc = list(nx.algorithms.dag.descendants(g, 't23'))
#print('desc', desc)
#g2 = g.subgraph(desc)
#
#all_paths = paths_dag.compute_paths(g2)
#p1 = paths_dag.expand_compressed_paths(g2, all_paths)
#print('n_total_paths', paths_dag.n_paths(p1))
#p2 = paths_dag.compute_paths_old(g2)
#assert paths_dag.expanded_path_to_comparable(p1) == paths_dag.expanded_path_to_comparable(p2)
#assert 0



#draw_graph(g, cut3)
#plt.show()
#test_graph(g)
#assert False


cut_edges = [('y17', 'y17s1', 0), ('z17', 'o17', 0), ('y10', 'y10s0', 0), ('y14', 'y14s0', 0), ('y2', 'y2s1', 0), ('y6', 'y6s1', 0), ('y3', 'y3s0', 0), ('z3', 'o3', 0), ('y13', 'y13s1', 0),
             ('y5', 'y5s1', 0), ('y11', 'y11s1', 0), ('y4', 'y4s1', 0), ('y1', 'y1s1', 0), ('x7', 'x7s1', 0), ('z15', 'o15', 0), ('z0', 'o0', 0), ('y12', 'y12s0', 0),
             ('y7', 'y7s1', 0), ('y8s0', 't15', 0), ('y8s0', 'z17', 0), ('t44s0', 'z9', 0), ('t44s1', 'z0', 0), ('y10s1', 't15', 0), ('y10s1', 'z8', 0), ('y2s0', 'z14', 0),
             ('y2s0', 't10', 0), ('t33s0', 't34', 0), ('t33s0', 'z2', 0), ('t33s0', 't35', 0), ('t33s0', 't42', 0), ('t33s0', 'z11', 0), ('t33s0', 't44', 0), ('t33s1', 't34', 0),
             ('t33s1', 'z2', 0), ('t33s1', 't35', 0), ('t33s1', 'z11', 0), ('t33s1', 't44', 0), ('t33s2', 't34', 0), ('t33s2', 't42', 0), ('t33s2', 'z11', 0), ('t33s2', 't44', 0),
             ('t33s3', 'z2', 0), ('t33s3', 't35', 0), ('t33s3', 't42', 0), ('t33s3', 'z11', 0), ('t33s3', 't44', 0), ('t33s4', 't34', 0), ('t33s4', 'z2', 0), ('t33s4', 't35', 0),
             ('t33s4', 't42', 0), ('t33s4', 'z11', 0), ('t33s4', 't44', 0), ('t33s5', 't34', 0), ('t33s5', 'z2', 0), ('t33s5', 't35', 0), ('t33s5', 't42', 0), ('t2s0', 't4', 0),
             ('t2s0', 't6', 0), ('t41s0', 't45', 0), ('t41s1', 'z8', 0), ('t41s1', 't45', 0), ('t41s1', 'z17', 0), ('t41s2', 'z8', 0), ('t41s2', 'z17', 0), ('y13s0', 't7', 0),
             ('y13s0', 'z12', 0), ('t45s0', 'z7', 0), ('t45s1', 'z16', 0), ('y15s0', 't2', 0), ('y15s1', 'z0', 0), ('t24s0', 't27', 0), ('t24s0', 't33', 0), ('t24s1', 't36', 0),
             ('t24s1', 't30', 0), ('t24s1', 't27', 0), ('t24s1', 't33', 0), ('t24s2', 't36', 0), ('t24s2', 't30', 0), ('t24s2', 't27', 0), ('t24s3', 't36', 0), ('t24s3', 't30', 0),
             ('t24s3', 't33', 0), ('t12s0', 't14', 0), ('t12s1', 't16', 0), ('t43s0', 'z3', 0), ('t43s1', 'z12', 0), ('t16s0', 't20', 0), ('t16s1', 't18', 0), ('t25s0', 't28', 0),
             ('t25s1', 't40', 0), ('t36s0', 't37', 0), ('t36s0', 't38', 0), ('t29s0', 't42', 0), ('t29s0', 't39', 0), ('t29s0', 'z5', 0), ('t29s0', 't43', 0), ('t29s1', 't42', 0),
             ('t29s1', 'z14', 0), ('t29s1', 't39', 0), ('t29s1', 'z5', 0), ('t29s1', 't43', 0), ('t29s2', 't42', 0), ('t29s2', 'z14', 0), ('t29s2', 't39', 0), ('t29s2', 't43', 0),
             ('t29s3', 'z14', 0), ('t29s3', 'z5', 0), ('t29s3', 't43', 0), ('t29s4', 't42', 0), ('t29s4', 'z14', 0), ('t29s4', 't39', 0), ('t29s4', 'z5', 0), ('y12s1', 't2', 0),
             ('y12s1', 'z9', 0), ('y9s0', 'z15', 0), ('y9s1', 't12', 0), ('t42s0', 'z6', 0), ('t42s1', 'z6', 0), ('t42s1', 'z15', 0), ('t42s1', 't45', 0), ('t42s2', 'z15', 0),
             ('t42s2', 't45', 0), ('y17s0', 'z7', 0), ('y17s1', 't13', 0), ('y14s1', 't13', 0), ('y14s1', 'z16', 0), ('y6s0', 't3', 0), ('y6s0', 'z1', 0), ('y3s1', 't3', 0),
             ('y3s1', 'z10', 0), ('t7s0', 't11', 0), ('t7s1', 't9', 0), ('t27s0', 't38', 0), ('t27s0', 't28', 0), ('t27s1', 't35', 0), ('t27s1', 't28', 0), ('t27s2', 't35', 0),
             ('t27s2', 't38', 0), ('y1s0', 'z4', 0), ('y1s0', 't8', 0), ('t40s0', 'z13', 0), ('t40s0', 't41', 0), ('t40s0', 't43', 0), ('t40s1', 'z4', 0), ('t40s1', 'z13', 0),
             ('t40s1', 't41', 0), ('t40s2', 'z4', 0), ('t40s2', 'z13', 0), ('t40s2', 't43', 0), ('t40s3', 'z4', 0), ('t40s3', 't41', 0), ('t40s3', 't43', 0), ('t22s0', 't25', 0),
             ('t22s0', 't31', 0), ('t22s1', 't31', 0), ('t22s1', 't29', 0), ('t22s2', 't25', 0), ('t22s2', 't29', 0), ('y7s0', 't10', 0), ('y7s0', 'z5', 0), ('t26s0', 't27', 0),
             ('t26s0', 't31', 0), ('t37s0', 'z10', 0), ('t37s0', 't41', 0), ('t37s0', 'z1', 0), ('t37s1', 'z10', 0), ('t37s1', 't44', 0), ('t37s1', 't41', 0), ('t37s2', 't44', 0),
             ('t37s2', 't41', 0), ('t37s2', 'z1', 0), ('t37s3', 'z10', 0), ('t37s3', 't44', 0), ('t37s3', 'z1', 0), ('y5s0', 't8', 0), ('y5s0', 'z13', 0), ('t14s0', 't17', 0),
             ('t14s0', 't19', 0), ('y11s0', 'z6', 0), ('y11s0', 't12', 0), ('y4s0', 't5', 0), ('y4s0', 'z11', 0), ('x7s0', 'z2', 0), ('x7s0', 't5', 0), ('t21s0', 't26', 0),
             ('t21s0', 't25', 0), ('y16s0', 'z3', 0), ('y16s0', 't7', 0), ('t23s0', 't34', 0), ('t23s0', 't30', 0), ('t23s1', 't34', 0), ('t23s1', 't26', 0), ('t23s2', 't26', 0),
             ('t23s2', 't30', 0)]

#g = utils.remove_edges_cut(g, cut_edges)
#g = utils.simplify_graph(g)
#print('start opt setup')
cut_edges = opt_sni.opt_sni(g, split_c)
g2 = utils.remove_edges_cut(g, cut_edges)

print('Cut is NI', paths_dag.test_graph_NI(g2))
print('Cut is SNI', paths_dag.test_graph_SNI(g2))

draw_graph(g, cut_edges)
#draw_graph(g)
plt.show()

g3 = utils.simplify_graph(g2, preserve_IO=False)
cut_edges = [x for x in cut_edges if x in g3.edges]
draw_graph(g3, cut_edges)
plt.show()

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

