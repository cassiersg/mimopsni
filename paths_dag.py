
import networkx as nx
import itertools

def _inline_single_path(path, all_paths):
    if len(path) == 1:
        return path
    else:
        e0, (src, dest, e_id) = path
        assert e_id is None
        sub_paths = all_paths[src][dest]
        if len(sub_paths) == 1:
            return [e0] + sub_paths[0]
        else:
            return path
        
def int_points(path):
    if len(path) <= 1:
        return []
    else:
        return [dest for src, dest, _ in path[:-1]]

def _inline_paths(node, dest, paths_recursive, all_paths, g):
    inlined_full = [_inline_single_path(path, all_paths) for path in paths_recursive]
    points2paths = {}
    for i, p in enumerate(inlined_full):
        for ip in int_points(p):
            points2paths.setdefault(ip, list()).append(i)
    path_map = list(range(len(paths_recursive)))
    for int_node in nx.topological_sort(g):
        if int_node in points2paths:
            paths = points2paths[int_node]
            paths_mapped = set(path_map[p] for p in paths)
            if len(paths_mapped) > 1:
                p0 = path_map[paths[0]]
                remaining = inlined_full[p0][int_points(inlined_full[p0]).index(int_node) + 1:]
                inlined_full[p0] = [(node, int_node, None)] + remaining
                for p in paths[1:]:
                    inlined_full[p] = None
                    path_map[p] = p0
    return [p for p in inlined_full if p is not None]

def compute_paths(g):
    paths_all = {}
    for node in reversed(list(nx.topological_sort(g))):
        paths = {}
        for _, succ, e_id in g.out_edges(node, keys=True):
            # simple edge
            paths.setdefault(succ, list()).append([(node, succ, e_id)])
            # composite path
            for dest in paths_all.get(succ, dict()).keys():
                paths.setdefault(dest, list()).append([(node, succ, e_id), (succ, dest, None)])
        for dest in nx.topological_sort(g):
            if dest in paths:
                paths_dest = paths[dest]
                paths_all.setdefault(node, dict())[dest] = _inline_paths(node, dest, paths_dest, paths_all, g)
    return paths_all

def is_graph_NI(g):
    paths = compute_paths(g)
    return all(len(l) <= 1 for src, p in paths.items() for _, l in p.items())

def is_graph_SNI(g):
    paths = compute_paths(g)
    for src in g.nodes:
        if g.nodes.data()[src].get('IN'):
            for dest in g.nodes:
                if g.nodes.data()[dest].get('OUT'):
                    if paths.get(src, {}).get(dest, []):
                        return False
    return all(len(l) <= 1 for src, p in paths.items() for _, l in p.items())

def _test_paths_comp(nodes, edges, res):
    g = nx.MultiDiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    assert compute_paths(g) == res

def _test_paths():
    print('start _test_paths')
    _test_paths_comp([0, 1], [(0, 1)],
                    {0: {1: [[(0, 1, 0)]]}})
    _test_paths_comp([0, 1, 2], [(0, 1), (1, 2)],
                    {0: {1: [[(0, 1, 0)]], 2: [[(0, 1, 0), (1, 2, 0)]]}, 1: {2: [[(1, 2, 0)]]}})
    _test_paths_comp([0, 1, 2], [(0, 1), (1, 2), (0, 2)],
                    {0: {1: [[(0, 1, 0)]], 2: [[(0, 1, 0), (1, 2, 0)], [(0, 2, 0)]]}, 1: {2: [[(1, 2, 0)]]}})
    _test_paths_comp(list(range(5)), [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)],
                    {0: {1: [[(0, 1, 0)]], 2: [[(0, 1, 0), (1, 2, 0)]], 3: [[(0, 1, 0), (1, 3, 0)]],
                         4: [[(0, 1, 0), (1, 4, None)]], 5: [[(0, 1, 0), (1, 4, None), (4, 5, 0)]]},
                     1: {2: [[(1, 2, 0)]], 3: [[(1, 3, 0)]], 4: [[(1, 2, 0), (2, 4, 0)], [(1, 3, 0), (3, 4, 0)]], 5: [[(1, 4, None), (4, 5, 0)]]},
                     2: {4: [[(2, 4, 0)]], 5: [[(2, 4, 0), (4, 5, 0)]]},
                     3: {4: [[(3, 4, 0)]], 5: [[(3, 4, 0), (4, 5, 0)]]},
                     4: {5: [[(4, 5, 0)]]}})
    _test_paths_comp(list(range(6)), [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6)],
                    {0: {1: [[(0, 1, 0)]], 2: [[(0, 1, 0), (1, 2, 0)]], 3: [[(0, 1, 0), (1, 3, 0)]], 4: [[(0, 1, 0), (1, 4, None)]],
                         5: [[(0, 1, 0), (1, 4, None), (4, 5, 0)]], 6: [[(0, 1, 0), (1, 4, None), (4, 5, 0), (5, 6, 0)]]},
                     1: {2: [[(1, 2, 0)]], 3: [[(1, 3, 0)]], 4: [[(1, 2, 0), (2, 4, 0)], [(1, 3, 0), (3, 4, 0)]],
                         5: [[(1, 4, None), (4, 5, 0)]], 6: [[(1, 4, None), (4, 5, 0), (5, 6, 0)]]},
                     2: {4: [[(2, 4, 0)]], 5: [[(2, 4, 0), (4, 5, 0)]], 6: [[(2, 4, 0), (4, 5, 0), (5, 6, 0)]]},
                     3: {4: [[(3, 4, 0)]], 5: [[(3, 4, 0), (4, 5, 0)]], 6: [[(3, 4, 0), (4, 5, 0), (5, 6, 0)]]},
                     4: {5: [[(4, 5, 0)]], 6: [[(4, 5, 0), (5, 6, 0)]]},
                     5: {6: [[(5, 6, 0)]]}})
    print('all _test_paths test succeded')

    nodes = list(range(6))
    edges = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
    g = nx.MultiDiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    from pprint import pprint
    print('start compute')
    pprint(compute_paths(g))

if __name__ == '__main__':
    _test_paths()
