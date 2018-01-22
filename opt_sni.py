
import networkx as nx
import pulp
import paths_dag
import pdb

from pprint import pprint

def opt_sni(g, split_c=tuple(), indep_bits=True):

    all_paths = paths_dag.compute_paths(g)
    #pprint('all_paths')
    #pprint(all_paths)
    #pdb.set_trace()

    edges = list(g.edges)
    e_ids = {e: i for i, e in enumerate(edges)}

    prob = pulp.LpProblem("edges", pulp.LpMinimize)
    #ecuts = pulp.LpVariable.dicts("ecut", range(len(edges)), 0, 1, pulp.LpInteger)
    ecuts = {i: pulp.LpVariable('ecut_{}_{}'.format(*edges[i][:2]), 0, 1, pulp.LpInteger) for i in range(len(edges))}
    prob += sum(ecuts.values()), "number of cut edges"

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
                            p_set_cuts[(n, d)] = pulp.LpVariable('p_cluster_{}_{}'.format(n, d), 0, 1, pulp.LpInteger)
                        c += p_set_cuts[(n, d)]
                    else:
                        c += ecuts[e_ids[(n, d, e_id)]]
                cur_p_cut = pulp.LpVariable('p_cut_{}_{}_{}'.format(src, dest, len(p_cuts[(src, dest)])), 0, 1)
                p_cuts[(src, dest)].append(cur_p_cut)
                # path constraint
                prob += cur_p_cut <= c
            min_n_cuts = len(all_paths[src][dest])
            if not (g.nodes[src].get('IN') and g.nodes[dest].get('OUT')):
                min_n_cuts -= 1
            # set of paths constraint
            prob += sum(p_cuts[(src, dest)]) >= min_n_cuts
    # clusters constraints
    for (src, dest), var in p_set_cuts.items():
        prob += len(all_paths[src][dest]) * var <= sum(p_cuts[(src, dest)])

    # split_c constraints
    for c in split_c:
        for s in g.successors(c[0]):
            prob += sum(ecuts[e_ids[(src, s, 0)]] for src in c) >= len(c)-1

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
        print('len', len(pcuts_in2dest))
        #pprint(pcuts_in2dest)
        for i, p_cuts2dest in enumerate(pcuts_in2dest.values()):
            prob += sum(p_cuts2dest) >= len(p_cuts2dest) - 1

    #prob.writeLP('aes.lp')
    print('Starting optimization...')
    prob.solve(pulp.PULP_CBC_CMD(msg=1, threads=4, maxSeconds=4*60*60))
    #prob.solve(pulp.PULP_CBC_CMD(threads=4, maxSeconds=900))
    #print('prob', repr(prob))
    #prob.solve(pulp.GLPK_CMD())
    #print('prob', dir(prob))
    for v in prob.variables():
        print(v, '=', v.value(), ',', end='')
    print('\n')
    #print(prob.variables())
    #print('solver', prob.solver)
    #print('solver', dir(prob.solver))
    #print('solver', prob.solver.__dict__)
    print("Status:", pulp.LpStatus[prob.status])
    cut_edges = [edges[i] for i, e in ecuts.items() if pulp.value(e) == 1.0]
    print("Cut edges:", cut_edges)
    return cut_edges

