
import networkx as nx
import matplotlib.pyplot as plt
import copy
import graph


def parse_assign(assign):
    dst, expr = assign.split('=')
    expr_n = expr.replace('*', '+')
    src1, src2 = expr_n.split('+')
    op = expr[expr_n.find('+')]
    return (dst, op, (src1, src2))

def flatten(x):
    return (z for y in x for z in y)

s = open('repr_aes_bitslice/non_lin.txt').read()
l = [parse_assign(x) for x in s.splitlines()]
nodes = set(flatten((dst, *srcs) for dst, op, srcs in l))
edges = list(flatten(((src1, dst), (src2, dst)) for dst, op, (src1, src2) in l))

s_out = open('repr_aes_bitslice/lin_out.txt').read()
l_out = [parse_assign(x) for x in s_out.splitlines()]
out_nodes = set(flatten(srcs for dst, op, srcs in l_out)) & nodes

dst_nodes = set(dst for dst, op, srcs in l)
in_nodes = nodes - dst_nodes

gaes = nx.MultiDiGraph()
gaes.add_nodes_from(nodes)
gaes.add_edges_from(edges)


#pos=nx.nx_agraph.graphviz_layout(gaes, prog='dot')
#nx.draw(gaes, pos, with_labels=True, arrows=True)

assert not in_nodes & out_nodes
assert not list(nx.simple_cycles(gaes))

for n in in_nodes: gaes.nodes[n]['IN'] = True
for n in out_nodes: gaes.nodes[n]['OUT'] = True

g2 = copy.deepcopy(gaes)
graph.simplify_graph(g2)

#pos=nx.nx_agraph.graphviz_layout(g2, prog='dot')
#nx.draw(g2, pos, with_labels=True, arrows=True)

cut = graph.opt_setup(g2)
graph.show_cut_graph(g2, cut)
plt.show()

