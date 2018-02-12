
"""
Parsing text representation of computation graphs.
"""

import networkx as nx

from utils import flatten

def parse_assignment(assignment):
    dst, expr = assignment.split('=')
    expr_n = expr.replace('*', '+')
    src1, src2 = expr_n.split('+')
    op = expr[expr_n.find('+')]
    return (dst, op, (src1, src2))

def parse_string_graph(s):
    """Parse a string representation of a computation graph into a graph

    String representation:
    one assignment per line, in the form
    z = x OP y
    where OP is + or * and  x, y, z are alphanumeric strings.
    Directed Acyclic Graph representation:
    One node for each variable, operator is attached to 'op' attribute of the
    node if variable appears in the LHS of an assignment. Two input edge for each
    assigned variable coming from operands.
    """
    l = [parse_assignment(x) for x in s.splitlines()]
    nodes = set(flatten((dst, *srcs) for dst, op, srcs in l))
    edges = list(flatten(
        ((src1, dst), (src2, dst)) for dst, op, (src1, src2) in l
    ))
    g = nx.MultiDiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    for dst, op, _ in l:
        g.nodes[dst]['op'] = op
    # Check is DAG
    assert not list(nx.simple_cycles(g))
    return g

def parse(
    s,
    tag_input_fn=lambda g, n: g.in_degree(n) == 0,
    tag_output_fn=lambda g, n: False,
    add_output_nodes=True,
    output_name_fn=lambda n: 'o'+n[1:],
    ):
    """Parse s, tag inputs and add tagged output nodes or tag outputs."""
    g = parse_string_graph(s)
    for n in list(g.nodes):
        if tag_input_fn(g, n):
            g.nodes[n]['IN'] = True
        if tag_output_fn(g, n):
            if add_output_nodes:
                name = output_name_fn(n)
                g.add_node(name)
                g.add_edge(n, name)
                g.nodes[name]['OUT'] = True
            else:
                g.nodes[n]['OUT'] = True
    # Sanity check
    assert not any(
        g.nodes[n].get('IN') and g.nodes[n].get('OUT') for n in g.nodes
    )
    return g

