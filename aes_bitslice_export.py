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
Export AES S-Box computation graph with cut edges to a LaTeX representation.
"""

import re

import networkx as nx

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
        ('y11s0', 'z6', 0), ('t40s2', 'z13', 0), ('t23s1', 't34', 0), ('y1s0', 't8', 0), ('t41s2', 'z17', 0), ('y5', 'y5s1', 0),
        ('y2', 'y2s1', 0), ('t24s3', 't27', 0), ('t16s0', 't18', 0), ('t29s4', 't39', 0), ('y17s0', 'z7', 0), ('t7s0', 't11', 0),
        ('t29s0', 'z5', 0), ('t44s0', 'z0', 0), ('z8', 'o8', 0), ('y4', 'y4s1', 0), ('t33s2', 't44', 0), ('y12', 'y12s1', 0),
        ('y15', 'y15s1', 0), ('t29', 't29s4', 0), ('t33s3', 't35', 0), ('t29s1', 't43', 0), ('t33s0', 't34', 0), ('y4s0', 'z11', 0),
        ('t25s1', 't40', 0), ('t41s1', 'z17', 0), ('t29s0', 't42', 0), ('t33s5', 'z11', 0), ('z9', 'o9', 0), ('y12s0', 'z9', 0),
        ('y3s0', 't3', 0), ('y10s0', 'z8', 0), ('t41s2', 't45', 0), ('t37s3', 't44', 0), ('y17', 'y17s1', 0), ('t24s2', 't33', 0),
        ('t33s1', 't34', 0), ('t37s0', 't41', 0), ('t22', 't22s2', 0), ('z12', 'o12', 0), ('t33s5', 't42', 0), ('y3', 'y3s1', 0),
        ('t37s2', 't44', 0), ('t42s2', 't45', 0), ('y10s0', 't15', 0), ('t33s4', 't35', 0), ('t29s0', 'z14', 0), ('y4s0', 't5', 0),
        ('t40s1', 't41', 0), ('t33s4', 't44', 0), ('t33s5', 'z2', 0), ('y7s0', 'z5', 0), ('t33s2', 'z2', 0), ('t40s2', 'z4', 0),
        ('y8s0', 't15', 0), ('t29s1', 't42', 0), ('y17s0', 't13', 0), ('t29s3', 't43', 0), ('t45s0', 'z7', 0), ('t42s1', 'z6', 0),
        ('y9s0', 't12', 0), ('t26s0', 't27', 0), ('t33s1', 't44', 0), ('t2s0', 't6', 0), ('t40s0', 'z4', 0), ('t23s0', 't26', 0),
        ('y3s0', 'z10', 0), ('t37s0', 'z1', 0), ('t41s0', 't45', 0), ('t14s0', 't17', 0), ('t33s3', 't44', 0), ('t37s2', 'z10', 0),
        ('t24s2', 't27', 0), ('t33s3', 't42', 0), ('y13s0', 'z12', 0), ('y12s0', 't2', 0), ('y7s0', 't10', 0), ('y13s0', 't7', 0),
        ('t33s2', 't42', 0), ('z6', 'o6', 0), ('y2s0', 't10', 0), ('t14s0', 't19', 0), ('z16', 'o16', 0), ('t22s1', 't29', 0),
        ('t33s0', 'z11', 0), ('z3', 'o3', 0), ('t41s2', 'z8', 0), ('t23s0', 't30', 0), ('t23s0', 't34', 0), ('t33s3', 'z2', 0),
        ('t29s2', 't42', 0), ('t27s1', 't38', 0), ('t42s1', 'z15', 0), ('t29s2', 't43', 0), ('t40', 't40s3', 0), ('t42s0', 't45', 0),
        ('t36', 't36s1', 0), ('t29s1', 'z5', 0), ('y7', 'y7s1', 0), ('y5s0', 'z13', 0), ('t27s1', 't35', 0), ('t27s0', 't28', 0),
        ('t40s1', 't43', 0), ('t24s0', 't36', 0), ('z7', 'o7', 0), ('t40s2', 't41', 0), ('y1', 'y1s1', 0), ('t43s1', 'z12', 0),
        ('t29s2', 'z5', 0), ('t27s2', 't35', 0), ('t33s3', 'z11', 0), ('t36s0', 't38', 0), ('y16s0', 'z3', 0), ('t40s2', 't43', 0),
        ('t33s5', 't44', 0), ('t29s3', 't42', 0), ('t33s4', 't42', 0), ('t29', 't29s2', 0), ('z4', 'o4', 0), ('y15s0', 't2', 0),
        ('y5s0', 't8', 0), ('x7', 'x7s1', 0), ('t37', 't37s3', 0), ('t24s3', 't30', 0), ('t33s2', 't35', 0), ('t37s2', 'z1', 0),
        ('t33s4', 'z11', 0), ('t33s1', 'z2', 0), ('t33s1', 't35', 0), ('x7s0', 'z2', 0), ('t42', 't42s0', 0), ('t12s0', 't14'    , 0),
        ('t12s1', 't16', 0), ('t40s1', 'z4', 0), ('t42s2', 'z6', 0), ('t44', 't44s1', 0), ('t37s1', 'z1', 0), ('y16s0', 't7', 0),
        ('t25s0', 't28', 0), ('t33s2', 'z11', 0), ('t29s3', 'z14', 0), ('t44s1', 'z9', 0), ('t33s4', 'z2', 0), ('y8', 'y8s1', 0),
        ('t24s1', 't36', 0), ('t29s0', 't43', 0), ('t24', 't24s1', 0), ('y14s0', 'z16', 0), ('t43s0', 'z3', 0), ('t27s1', 't28', 0),
        ('y14s0', 't13', 0), ('y2s0', 'z14', 0), ('t40s0', 'z13', 0), ('t24s3', 't33', 0), ('y9s0', 'z15', 0), ('t23s1', 't30', 0),
        ('t41s0', 'z8', 0), ('t33s5', 't35', 0), ('y9', 'y9s1', 0), ('t29s3', 'z5', 0), ('t24s0', 't33', 0), ('t22s0', 't31', 0),
        ('t40s0', 't41', 0), ('y1s0', 'z4', 0), ('t26', 't26s1', 0), ('y15s0', 'z0', 0), ('t7s0', 't9', 0), ('x7s0', 't5', 0),
        ('t29s3', 't39', 0), ('t42s2', 'z15', 0), ('y16', 'y16s1', 0), ('t37s2', 't41', 0), ('t24s3', 't36', 0), ('t37s0', 'z10', 0),
        ('t33s3', 't34', 0), ('y14', 'y14s1', 0), ('y13', 'y13s1', 0), ('t33s4', 't34', 0), ('t29s1', 'z14', 0), ('t24s2', 't30', 0),
        ('y8s0', 'z17', 0), ('t37s1', 't41', 0), ('y6s0', 'z1', 0), ('t22s2', 't29', 0), ('t24s0', 't30', 0), ('y11', 'y11s1', 0),
        ('y10', 'y10s1', 0), ('t26s0', 't31', 0), ('t22s1', 't25', 0), ('t2s0', 't4', 0), ('t21', 't21s1', 0), ('t37s3', 'z10', 0),
        ('t33', 't33s0', 0), ('t24s0', 't27', 0), ('t33s2', 't34', 0), ('t27s2', 't38', 0), ('t21s0', 't26', 0), ('t40s1', 'z13', 0),
        ('y11s0', 't12', 0), ('t29s0', 't39', 0), ('t37s1', 't44', 0), ('t40s0', 't43', 0), ('t16s1', 't20', 0), ('t33s1', 't42', 0),
        ('t29s1', 't39', 0), ('y6', 'y6s1', 0), ('z10', 'o10', 0), ('t22s1', 't31', 0), ('t32', 't33', 0), ('t29s4', 'z14', 0),
        ('t22s0', 't25', 0), ('t23s1', 't26', 0), ('t21s0', 't25', 0), ('z17', 'o17', 0), ('t36s0', 't37', 0), ('t45s0', 'z16', 0),
        ('y6s0', 't3', 0)]

nok = [x for x in cut_edges if ' ' in x[0]+x[1]]
assert not nok, nok

print(len(cut_edges))

def rename_split(g, cut, split_c_d):
    rename = dict()
    for n, sg in split_c_d.items():
        sg = [s for s in sg if s in g.nodes]
        rename.update((s, f'{n}s{i}') for i, s in enumerate(sg))
    return rename


def export_graph(g, cut, split_c_d):
    cut = {(x, y) for x, y, *_ in cut}
    rename = rename_split(g, cut, split_c_d)

    def mn(n):
        return rename.get(n, n)

    def test_refresh(src, dest):
        return f"\\refresh({format_var(mn(src))})" if (src, dest) in cut else format_var(mn(src))

    for n in nx.topological_sort(g):
        pred = list(g.predecessors(n))
        if len(pred) == 0:
            assert 'op' not in g.nodes[n], f"{n}, {g.nodes[n]['op']}"
        elif len(pred) == 1:
            assert 'op' not in g.nodes[n], f"{n}, {g.nodes[n]['op']}"
            yield format_var(mn(n)) + "=" + test_refresh(pred[0], n)
        elif len(pred) == 2:
            op = g.nodes[n]['op']
            o1 = test_refresh(pred[0], n)
            o2 = test_refresh(pred[1], n)
            op = op.replace('*', r'\cdot')
            yield format_var(mn(n)) + " = " + o1 + f' {op} ' + o2
        else:
            raise ValueError(f"{n}, {pred}")

def format_var(l):
    re_var = r'([a-z])([0-9]+)([a-z]?)([0-9]*)'
    res = re.match(re_var, l)
    assert res, l
    n0, n1, n2, n3 = res.groups()
    sp_comp = ',' + n3 if n2 else ''
    #sp_comp = ',' + n2 + '_{' + n3 + '}' if n2 else ''
    return n0 + '_{' + n1 +  sp_comp + '}'

def format_assign(l):
    if 'not' in l:
        re_var_simple = r'[a-z][0-9]+'
        res = re.match(f'({re_var_simple})=not\\(({re_var_simple})(\\*|\\+)({re_var_simple})\\)', l)
        assert res, l
        dest, src1, op, src2 = res.groups()
        op = op.replace('*', r'\cdot')
        res = format_var(dest) + ' = \\lognot(' + format_var(src1) + f' {op} ' + format_var(src2) + ')'
    else:
        dest, op, (src1, src2) = parse.parse_assignment(l)
        op = op.replace('*', r'\cdot')
        res = format_var(dest) + ' = ' + format_var(src1) + f' {op} ' + format_var(src2)
    return f'${res}$ \\\\'

def sort_assign(l):
    def k(s):
        "$X_{DD}..."
        s = s[1:]
        return (s[0], int(''.join(filter(str.isdigit, s[3:5]))), s[5:].replace(',', 'z').replace('}', 'a'))
    return list(sorted(l, key=k))

g4, simplified_cut_edges = graph_tools.without_unncessary_splits(g, cut_edges, split_c_d)
print(len(simplified_cut_edges))
exp = list(export_graph(g4, simplified_cut_edges, split_c_d))
exp = sort_assign(f'${x}$ \\\\' for x in exp)
exp_old = exp
exp = (
        [x for x in exp if x.startswith('$x')] +
        [x for x in exp if x.startswith('$y')] +
        [x for x in exp if x.startswith('$t')] +
        [x for x in exp if x.startswith('$z')] +
        [x for x in exp if x.startswith('$o')]
        )
s_in = open('repr_aes_bitslice/lin_in.txt').read()
s_out = open('repr_aes_bitslice/lin_out_not.txt').read()
s_out = s_out.replace('z', 'o')
exp_out = sort_assign(map(format_assign, s_out.splitlines()))
exp_out = (
        [x for x in exp_out if x.startswith('$t')] +
        [x for x in exp_out if x.startswith('$s')]
        )
s = (
        '\\begin{multicols}{5}\n' +
        '[Top linear layer\n]\n' +
        r'\noindent' +
        '\n'.join(sort_assign(map(format_assign, s_in.splitlines()))) + '\n' +
        '\\end{multicols}\n\n' +
        '\\begin{multicols}{5}\n' +
        '[Middle non-linear layer\n]\n' +
        r'\noindent' +
        '\n'.join(exp) + '\n' +
        '\\end{multicols}\n\n' +
        '\\begin{multicols}{5}\n' +
        '[Bottom linear layer\n]\n' +
        r'\noindent' +
        '\n'.join(exp_out) + '\n' +
        '\\end{multicols}\n'
        )
print(s)

