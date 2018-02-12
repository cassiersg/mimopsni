
import networkx as nx
import pulp
import paths_dag

def opt_sni(g, split_c=tuple(), indep_bits=True, max_seconds=4*60):
    """
    Compute an optimized set of edges in g to be refreshed in order to get
    (MIMO-)SNI.

    g: computation graph
    split_c: dict {operation_node: [list of split nodes under it]}
        spliit nodes for a given operation node are assumed to form a complete
        DAG layer
    indep_bits: if True: optimize for MIMO-SNI, else optimize for SNI
    max_second: time limit passed to the optimizer
    """

    # compute all paths in the graph, in "cluster" form
    all_paths = paths_dag.compute_paths(g)

    # linear problem
    prob = pulp.LpProblem("edges", pulp.LpMinimize)
    # variables for edge cuts
    ecuts = {edge: pulp.LpVariable('ecut_{}_{}'.format(*edge[:2]), 0, 1, pulp.LpInteger) for edge in g.edges}
    # objective function
    prob += sum(ecuts.values()), "number of cut edges"

    # adding constraints
    p_set_cuts = {}
    p_cuts = {}

    for src in all_paths:
        for dest in all_paths[src]:
            p_cuts[(src, dest)] = []
            for path in all_paths[src][dest]:
                c = 0
                for n, d, e_id in path:
                    if e_id is None:
                        if (n, d) not in p_set_cuts:
                            # variable for path cluster cut
                            p_set_cuts[(n, d)] = pulp.LpVariable('p_cluster_{}_{}'.format(n, d), 0, 1, pulp.LpInteger)
                        c += p_set_cuts[(n, d)]
                    else:
                        c += ecuts[(n, d, e_id)]
                # variable for path cut
                cur_p_cut = pulp.LpVariable('p_cut_{}_{}_{}'.format(src, dest, len(p_cuts[(src, dest)])), 0, 1)
                p_cuts[(src, dest)].append(cur_p_cut)
                # path constraint
                prob += cur_p_cut <= c
            min_n_cuts = len(all_paths[src][dest])
            # adapt constraint for I-O paths -> to get SNI, not only NI
            if not (g.nodes[src].get('IN') and g.nodes[dest].get('OUT')):
                min_n_cuts -= 1
            # set of paths constraint
            prob += sum(p_cuts[(src, dest)]) >= min_n_cuts
    # clusters of paths constraints
    for (src, dest), var in p_set_cuts.items():
        prob += len(all_paths[src][dest]) * var <= sum(p_cuts[(src, dest)])

    # split_c constraints
    # force to cut a constant number of edges around split nodes
    for c in split_c:
        for s in g.successors(c[0]):
            prob += sum(ecuts[(src, s, 0)] for src in c) >= len(c)-1

    # *MIMO*-SNI constraints
    if indep_bits:
        # cut all but 1 paths from any node to all outputs
        for src in all_paths:
            p_cuts2dest = sum(
                (p_cuts[(src, dest)] for dest in all_paths[src]
                 if g.nodes[dest].get('OUT')),
                []
            )
            prob += sum(p_cuts2dest) >= len(p_cuts2dest) - 1
        [(dest, src) for src in all_paths for dest in all_paths[src] if g.nodes[src].get('IN')]
        # cut all but 1 paths from all inputs to any node
        pcuts_in2dest = {}
        for src in all_paths:
            if g.nodes[src].get('IN'):
                for dest in all_paths[src]:
                    pcuts_in2dest.setdefault(dest, []).extend(p_cuts[(src, dest)])
        for i, p_cuts2dest in enumerate(pcuts_in2dest.values()):
            prob += sum(p_cuts2dest) >= len(p_cuts2dest) - 1

    print('Starting optimization...')
    #prob.solve(pulp.PULP_CBC_CMD(msg=1, threads=4, maxSeconds=max_seconds))
    prob.solve(pulp.solvers.CPLEX(msg=1, timeLimit=max_seconds))
    for v in prob.variables():
        assert v.value() in (0.0, 1.0), 'non-integer variable: {} = {}'.format(v, v.value())
    print('\n')
    print("Status:", pulp.LpStatus[prob.status])
    cut_edges = [edge for edge, ecut in ecuts.items() if pulp.value(ecut) == 1.0]
    print("Cut edges:", cut_edges)
    return cut_edges

