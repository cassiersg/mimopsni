
import math
import itertools as it
import random

import networkx as nx

import utils


class Circuit:
    def __init__(self):
        self.vars = []
        self.bijs = []
        self.p_bijs = []
        self.l_sums = []
        self.p_sums = []
        self.l_prods = []
        self.p_prods = []

    def var(self, name, continuous=False, kind='intermediate'):
        v = Variable(name, len(self.vars), continuous, kind)
        self.vars.append(v)
        return v

    def bij(self, dest, op):
        self.bijs.append((dest, op))

    def p_bij(self, dest, op):
        self.p_bijs.append((dest, op))

    def l_sum(self, dest, ops):
        assert isinstance(dest, Variable) and all(isinstance(op, Variable) for op in ops)
        self.l_sums.append((dest, ops))

    def p_sum(self, dest, ops):
        assert isinstance(dest, Variable) and all(isinstance(op, Variable) for op in ops)
        self.p_sums.append((dest, ops))

    def l_prod(self, dest, ops):
        assert isinstance(dest, Variable) and all(isinstance(op, Variable) for op in ops)
        self.l_prods.append((dest, ops))

    def p_prod(self, dest, ops):
        assert isinstance(dest, Variable) and all(isinstance(op, Variable) for op in ops)
        self.p_prods.append((dest, ops))

    def fmt_var(self, var):
        fmt_specifier = '{{:0{}}}_{{}}'.format(math.ceil(math.log10(len(self.vars))))
        return fmt_specifier.format(var.idx, var.name)

    def fmt_op(self, dest, ops, op, qual):
        return f'{qual} {self.fmt_var(dest)} = ' + f' {op} '.join(
                map(self.fmt_var, ops))

    def fmt_bij(self, ops):
        return 'B ' + ' '.join(map(self.fmt_var, ops))

    def fmt_cont(self, var):
        return 'C ' + self.fmt_var(var)

    def __str__(self):
        return '\n'.join(it.chain(
                (self.fmt_op(dest, ops, '+', 'L') for dest, ops, in self.l_sums),
                (self.fmt_op(dest, ops, '+', 'P') for dest, ops, in self.p_sums),
                (self.fmt_op(dest, ops, '*', 'L') for dest, ops, in self.l_prods),
                (self.fmt_op(dest, ops, '*', 'P') for dest, ops, in self.p_prods),
                map(self.fmt_bij, self.bijs + self.p_bijs),
                (self.fmt_cont(var) for var in self.vars if var.continuous),
                ))

    def simplified(self):
        map_vars = list(range(len(self.vars)))
        rev_map_vars = list({x} for x in range(len(self.vars)))
        for dest, op in self.bijs + self.p_bijs:
            idxs = (map_vars[dest.idx], map_vars[op.idx])
            to_merge = max(idxs)
            merge_into = min(idxs)
            if to_merge != merge_into:
                for v in rev_map_vars[to_merge]:
                    map_vars[v] = merge_into
                rev_map_vars[merge_into] |= rev_map_vars[to_merge]
                rev_map_vars[to_merge] = None
        rem_vars = [i for i, rv in enumerate(rev_map_vars) if rv is not None]
        nm = {v: i for i, v in enumerate(rem_vars)}
        final_map = [nm[mv] for mv in map_vars]
        new_c = Circuit()
        for v in rem_vars:
            continuous = any(self.vars[ov].continuous for ov in rev_map_vars[v])
            if any(self.vars[ov].kind == 'input' for ov in rev_map_vars[v]):
                kind = 'input'
            elif any(self.vars[ov].kind == 'random' for ov in rev_map_vars[v]):
                kind = 'random'
            else:
                kind = 'intermediate'
            new_c.var(self.vars[v].name, continuous, kind)
        for attr in ('l_sums', 'p_sums', 'l_prods', 'p_prods'):
            setattr(new_c,
                    attr,
                    [(new_c.vars[final_map[dest.idx]], [new_c.vars[final_map[op.idx]] for op in ops])
                        for (dest, ops) in getattr(self, attr)])
        return new_c, final_map

    def var_leakage(self, rand_var_leak=1, only_inputs_leak=False):
        leakage = [rand_var_leak*int(var.kind == 'random') for var in self.vars]
        #leakage = [0]*len(self.vars)
        for dest, ops in self.l_sums + self.l_prods:
            leakage[dest.idx] += 1
            for op in ops:
                leakage[op.idx] += 1
        if only_inputs_leak:
            leakage = [l if v.kind == 'input' else 0 for l, v in
                    zip(leakage, self.vars)]
        return leakage

    def to_lkm(self, rand_var_leak=1, only_inputs_leak=False):
        sc, var_map = self.simplified()
        is_cont = [v.continuous for v in sc.vars]
        leakage = sc.var_leakage(rand_var_leak, only_inputs_leak)
        ops = ([(0, [v.idx for v in (dest, *ops)]) for dest, ops in
                (sc.p_sums if only_inputs_leak else sc.l_sums + sc.p_sums)] +
               [(1, [v.idx for v in (dest, *ops)]) for dest, ops in
                (sc.p_sums if only_inputs_leak else sc.l_prods + sc.p_prods)])
        final_var_map = {self.fmt_var(v): var_map[v.idx] for v in self.vars}
        return (is_cont, leakage, ops), final_var_map

    def nb_randoms(self):
        return len([v for v in self.vars if v.kind == 'random'])

    def nb_ops(self):
        return len(self.l_sums) + len(self.l_prods)

    def cost(self, cost_random, cost_op):
        return self.nb_randoms()*cost_random + self.nb_ops()*cost_op


class Variable:
    def __init__(self, name, idx, continuous, kind):
        self.name = name
        self.idx = idx
        self.continuous = continuous
        self.kind = kind

class CompGraph:
    def __init__(self, circuit, domain=(0, 1)):
        self.g = nx.DiGraph()
        self.circuit = circuit
        self.domain = domain
        self.build_graph()

    def build_graph(self):
        for var in self.circuit.vars:
            self.g.add_node(var.idx)
            if var.kind == 'input':
                self.g.nodes[var.idx]['input'] = True
            elif var.kind == 'random':
                self.g.nodes[var.idx]['random'] = True
        for (dest, ops) in self.circuit.p_sums + self.circuit.l_sums:
            self.g.nodes[dest.idx]['op'] = '+'
            for op in ops:
                self.g.add_edge(op.idx, dest.idx)
        for (dest, ops) in self.circuit.p_prods + self.circuit.l_prods:
            self.g.nodes[dest.idx]['op'] = '*'
            for op in ops:
                self.g.add_edge(op.idx, dest.idx)
        for (dest, op) in self.circuit.bijs:
            self.g.nodes[dest.idx]['op'] = '='
            self.g.add_edge(op.idx, dest.idx)
        for node, attrs in self.g.nodes.items():
            assert 'input' in attrs or 'random' in attrs or 'op' in attrs, f'noinput node {self.circuit.fmt_var(self.circuit.vars[node])}'

    def map_inputs(self, inputs):
        return {next(var.idx for var in self.circuit.vars if var.name == name): v
                for name, v in inputs.items()}

    def compute(self, inputs):
        inputs = self.map_inputs(inputs)
        values = [None for _ in self.circuit.vars]
        for idx, v in inputs.items():
            values[idx] = v
        for var in self.circuit.vars:
            if var.kind == 'random':
                values[var.idx] = random.choice(self.domain)
        for idx in nx.topological_sort(self.g):
            if values[idx] is None:
                op = {'+': sum, '*': utils.product, '=': sum}[self.g.nodes[idx]['op']]
                values[idx] = op(values[pred] for pred in self.g.predecessors(idx))
        output_res = {
            var.idx: values[var.idx] for var in self.circuit.vars
            if var.kind == 'output'
            }
        return output_res, values

