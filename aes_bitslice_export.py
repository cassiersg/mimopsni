
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

cut_edges = [
        ('y14', 'y14s1', 0), ('z7', 'o7', 0), ('t37', 't37s2', 0), ('t29', 't29s2', 0), ('y3', 'y3s1', 0), ('y9', 'y9s1', 0),
        ('t40', 't40s1', 0), ('t40', 't40s2', 0), ('t25', 't25s1', 0), ('y4', 'y4s1', 0), ('t22', 't22s0', 0), ('t32', 't33', 0),
        ('y15', 'y15s1', 0), ('z12', 'o12', 0), ('y10', 'y10s0', 0), ('t45', 't45s0', 0), ('t42', 't42s0', 0), ('t44', 't44s0', 0),
        ('y6', 'y6s1', 0), ('z0', 'o0', 0), ('y5', 'y5s0', 0), ('t20', 't24', 0), ('y16', 'y16s1', 0), ('x7', 'x7s1', 0),
        ('t7', 't7s1', 0), ('t27', 't27s1', 0), ('y1', 'y1s1', 0), ('y11', 'y11s0', 0), ('t23', 't23s1', 0), ('z8', 'o8', 0),
        ('t33', 't33s2', 0), ('t18', 't22', 0), ('y2', 'y2s1', 0), ('y12', 'y12s1', 0), ('y17', 'y17s0', 0), ('y7', 'y7s1', 0),
        ('z17', 'o17', 0), ('t21', 't21s1', 0), ('t24', 't24s2', 0), ('y14s0', 't13', 0), ('y14s0', 'z16', 0), ('t37s0', 'z10', 0),
        ('t37s0', 't44', 0), ('t37s0', 't41', 0), ('t37s0', 'z1', 0), ('t37s1', 'z10', 0), ('t37s1', 't44', 0), ('t37s1', 't41', 0),
        ('t37s1', 'z1', 0), ('t37s2', 'z10', 0), ('t37s3', 'z10', 0), ('t37s3', 't44', 0), ('t37s3', 't41', 0), ('t37s3', 'z1', 0),
        ('y13s0', 't7', 0), ('y13s0', 'z12', 0), ('t29s0', 't42', 0), ('t29s0', 'z14', 0), ('t29s0', 't39', 0), ('t29s0', 't43', 0),
        ('t29s1', 't42', 0), ('t29s1', 'z14', 0), ('t29s1', 't39', 0), ('t29s1', 'z5', 0), ('t29s1', 't43', 0), ('t29s2', 'z5', 0),
        ('t29s3', 't42', 0), ('t29s3', 'z14', 0), ('t29s3', 't39', 0), ('t29s3', 'z5', 0), ('t29s3', 't43', 0), ('t29s4', 't42', 0),
        ('t29s4', 'z14', 0), ('t29s4', 't39', 0), ('t29s4', 'z5', 0), ('t29s4', 't43', 0), ('y3s0', 't3', 0), ('y3s0', 'z10', 0),
        ('t26s1', 't27', 0), ('t26s1', 't31', 0), ('t16s0', 't20', 0), ('t16s1', 't18', 0), ('y9s0', 't12', 0), ('y9s0', 'z15', 0),
        ('t40s0', 'z4', 0), ('t40s0', 'z13', 0), ('t40s0', 't41', 0), ('t40s0', 't43', 0), ('t40s1', 'z13', 0), ('t40s2', 'z4', 0),
        ('t40s2', 't41', 0), ('t40s2', 't43', 0), ('t40s3', 'z4', 0), ('t40s3', 'z13', 0), ('t40s3', 't41', 0), ('t40s3', 't43', 0),
        ('y8s0', 'z17', 0), ('y8s1', 't15', 0), ('t25s0', 't40', 0), ('t25s0', 't28', 0), ('y4s0', 't5', 0), ('y4s0', 'z11', 0),
        ('t22s0', 't25', 0), ('t22s1', 't31', 0), ('t22s1', 't29', 0), ('t22s2', 't25', 0), ('t22s2', 't31', 0), ('t22s2', 't29', 0),
        ('y15s0', 't2', 0), ('y15s0', 'z0', 0), ('y10s1', 't15', 0), ('y10s1', 'z8', 0), ('t45s1', 'z7', 0), ('t45s1', 'z16', 0),
        ('t36s0', 't37', 0), ('t36s0', 't38', 0), ('t42s0', 'z6', 0), ('t42s1', 'z6', 0), ('t42s1', 'z15', 0), ('t42s1', 't45', 0),
        ('t42s2', 'z6', 0), ('t42s2', 'z15', 0), ('t42s2', 't45', 0), ('t44s1', 'z9', 0), ('t44s1', 'z0', 0), ('y6s0', 't3', 0),
        ('y6s0', 'z1', 0), ('t2s1', 't4', 0), ('t2s1', 't6', 0), ('y5s1', 't8', 0), ('y5s1', 'z13', 0), ('y16s0', 'z3', 0),
        ('y16s0', 't7', 0), ('x7s0', 'z2', 0), ('x7s0', 't5', 0), ('t7s0', 't9', 0), ('t7s0', 't11', 0), ('t27s0', 't35', 0),
        ('t27s0', 't38', 0), ('t27s0', 't28', 0), ('t27s1', 't38', 0), ('t27s2', 't35', 0), ('t27s2', 't28', 0), ('y1s0', 'z4', 0),
        ('y1s0', 't8', 0), ('y11s1', 'z6', 0), ('y11s1', 't12', 0), ('t23s0', 't34', 0), ('t23s0', 't26', 0), ('t23s1', 't30', 0),
        ('t23s2', 't34', 0), ('t23s2', 't26', 0), ('t23s2', 't30', 0), ('t41s0', 'z8', 0), ('t41s0', 't45', 0), ('t41s1', 't45', 0),
        ('t41s1', 'z17', 0), ('t41s2', 'z8', 0), ('t41s2', 'z17', 0), ('t12s0', 't16', 0), ('t12s1', 't14', 0), ('t33s0', 'z2', 0),
        ('t33s0', 't35', 0), ('t33s0', 't42', 0), ('t33s0', 't44', 0), ('t33s1', 't34', 0), ('t33s1', 'z2', 0), ('t33s1', 't35', 0),
        ('t33s1', 't42', 0), ('t33s1', 'z11', 0), ('t33s1', 't44', 0), ('t33s2', 't34', 0), ('t33s2', 'z11', 0), ('t33s2', 't44', 0),
        ('t33s3', 't34', 0), ('t33s3', 'z2', 0), ('t33s3', 't35', 0), ('t33s3', 't42', 0), ('t33s3', 'z11', 0), ('t33s3', 't44', 0),
        ('t33s4', 't34', 0), ('t33s4', 'z2', 0), ('t33s4', 't35', 0), ('t33s4', 't42', 0), ('t33s4', 'z11', 0), ('t33s5', 't34', 0),
        ('t33s5', 'z2', 0), ('t33s5', 't35', 0), ('t33s5', 't42', 0), ('t33s5', 'z11', 0), ('t33s5', 't44', 0), ('t14s1', 't17', 0),
        ('t14s1', 't19', 0), ('t43s0', 'z3', 0), ('t43s1', 'z3', 0), ('t43s1', 'z12', 0), ('y2s0', 'z14', 0), ('y2s0', 't10', 0),
        ('y12s0', 't2', 0), ('y12s0', 'z9', 0), ('y17s1', 'z7', 0), ('y17s1', 't13', 0), ('y7s0', 't10', 0), ('y7s0', 'z5', 0),
        ('t21s0', 't26', 0), ('t21s0', 't25', 0), ('t24s0', 't30', 0), ('t24s0', 't27', 0), ('t24s0', 't33', 0), ('t24s1', 't36', 0),
        ('t24s1', 't30', 0), ('t24s1', 't27', 0), ('t24s1', 't33', 0), ('t24s2', 't36', 0), ('t24s3', 't36', 0), ('t24s3', 't30', 0),
        ('t24s3', 't27', 0), ('t24s3', 't33', 0)
        ]

def export_graph(g, cut):
    cut = {(x, y) for x, y, *_ in cut}

    def test_refresh(src, dest):
        return f"refresh({src})" if (src, dest) in cut else src

    for n in nx.topological_sort(g):
        pred = list(g.predecessors(n))
        if len(pred) == 0:
            assert 'op' not in g.nodes[n], f"{n}, {g.nodes[n]['op']}"
        elif len(pred) == 1:
            assert 'op' not in g.nodes[n], f"{n}, {g.nodes[n]['op']}"
            yield n + "=" + test_refresh(pred[0], n)
        elif len(pred) == 2:
            op = g.nodes[n]['op']
            o1 = test_refresh(pred[0], n)
            o2 = test_refresh(pred[1], n)
            yield n + "=" + o1 + op + o2
        else:
            raise ValueError(f"{n}, {pred}")

g4, simplified_cut_edges = graph_tools.without_unncessary_splits(g, cut_edges, split_c_d)
exp = export_graph(g4, simplified_cut_edges)
exp = (
        [x for x in exp if x.startswith('t')] + 
        [x for x in exp if x.startswith('z')] +
        [x for x in exp if x.startswith('o')]
        )
s_in = open('repr_aes_bitslice/lin_in.txt').read()
s_out = open('repr_aes_bitslice/lin_out_not.txt').read()
s_out = s_out.replace('z', 'o')
s = (
        'lin in\n' +
        '\n'.join(sorted(s_in.splitlines())) + '\n' +
        'non lin\n' +
        '\n'.join(exp) + '\n' +
        'lin out\n' +
        '\n'.join(sorted(s_out.splitlines())) + '\n'
        )
print(s)

