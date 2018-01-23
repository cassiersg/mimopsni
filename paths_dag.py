
import networkx as nx
import itertools

def _inline_single_path(path, all_paths):
    """Inline a path.

    * path must be in primitive recursive form:
    [(src, n1, e_id1), (n1, dest, None)]
    * all_paths must contain all paths in the graph that
    start at node n1, in aggregated and inlined form.

    If there is only one node from n1 to dest, the inlining returns
    an inlined representation of the path:
    [(src, n1, e_id1), edges of the path from n1 to dest]
    otherwise, path is returned unchanged (since inlining would generate
    multiple paths.
    """
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
    """Returns interior points in a path

    Interior points are all the points that appear explicitely in the path
    (we do not recurse into aggregated segments), except the source and the
    destination.
    """
    return [dest for src, dest, _ in path[:-1]]

def _aggregate_inline_multipath(src, dest, paths_recursive, all_paths, g):
    """Aggregates a list of paths from src to dest into a list of multipaths.

    The aggregation of some paths happens when they share common segments.
    """
    inlined_full = [_inline_single_path(path, all_paths) for path in paths_recursive]

    points2paths = {} # {ip: [paths having ip as interior point}
    for i, p in enumerate(inlined_full):
        for ip in int_points(p):
            points2paths.setdefault(ip, list()).append(i)

    # Iteratively aggregate paths that have a common intermediate point.
    # Update one of the aggregated paths in inlined_full with the new segment
    # replacing the edges and set all the other aggregated paths to None.
    # path_map keep a mapping from initial inlined_full index of a path (which
    # is still its id in points2paths) and the current multipath that contains
    # it.
    path_map = list(range(len(paths_recursive)))
    for int_node in nx.topological_sort(g):
        if int_node in points2paths:
            paths_with_ip = points2paths[int_node]
            paths_mapped = set(path_map[p] for p in paths_with_ip)
            if len(paths_mapped) > 1:
                # aggregate: select new common path
                p0 = path_map[paths_with_ip[0]]
                # since we have all paths from src to dest and since inlining keeps
                # paths with common final segments grouped, all paths have the same tail
                tail = inlined_full[p0][int_points(inlined_full[p0]).index(int_node) + 1:]
                # assertion disable for performance
                #for p in (path_map[x] for x in paths_with_ip):
                #    assert inlined_full[p][int_points(inlined_full[p]).index(int_node) + 1:] == tail
                # update tables
                inlined_full[p0] = [(src, int_node, None)] + tail
                for p in paths_with_ip[1:]:
                    inlined_full[p] = None
                    path_map[p] = p0
    return [p for p in inlined_full if p is not None]

def compute_paths(g):
    """Compute all the paths in a DAG g.

    Result is returned as
    {src_node1: {
        dest_node1: [
            mpath1, mpath2, ...
        ],
        dest_node2: ...
        },
     src_node2: ...
    }
    where each multipath 'mpath' represents a set of paths
    from src to dest.
    For efficiency reasons, not all paths are listed explicitely,
    the paths are rather aggregated into multipaths, which are paths
    that share some common edges.
    The multipath is a sequence of consecutive segments:
    mpath = [(src, n1, e_id1), (n1, n2, e_id2), ..., (nx, dest, eid(x+1))]
    where the segment (nx, n(x+1), e_id(x+1)) is:
        - the edge (nx, n(x+1), e_id(x+1)) of g if e_id(x+1) is an integer
        - any path between nx and n(x+1) if e_id(x+1) is None
    The multipath reprensents hence 2^{number of e_id(x) that are None}
    distinct paths.
    """
    all_paths = {}
    for src in reversed(list(nx.topological_sort(g))):
        paths_from_src = {}
        # list successors of src
        for _, succ, e_id in g.out_edges(src, keys=True):
            # path of one edge from src to succ
            paths_from_src.setdefault(succ, list()).append([(src, succ, e_id)])
            # composite multipath
            # Reverse topological order for iteration over src ensures
            # that all paths starting at succ are already computed.
            for dest in all_paths.get(succ, dict()).keys():
                paths_from_src.setdefault(dest, []).append([(src, succ, e_id), (succ, dest, None)])
        # aggregate distinct paths into one multipath if they and with the same edge
        # also inline unnecessarily recursive paths
        for dest in nx.topological_sort(g):
            if dest in paths_from_src:
                paths_from_src_to_dest = paths_from_src[dest]
                all_paths.setdefault(src, dict())[dest] = _aggregate_inline_multipath(
                    src, dest, paths_from_src_to_dest, all_paths, g)
    return all_paths

def is_graph_NI(g):
    desc = {}
    return True
    for n in reversed(list(nx.topological_sort(g))):
        desc.setdefault(n, set())
        for n2 in g.successors(n):
            if n2 in desc[n]:
                return False
            desc[n] |= set([n2])
            if desc[n] & desc[n2]:
                return False
            desc[n] |= desc[n2]
    return True

def is_graph_SNI(g):
    desc = {}
    for n in reversed(list(nx.topological_sort(g))):
        desc.setdefault(n, set())
        for n2 in g.successors(n):
            if n2 in desc[n]:
                return False
            desc[n] |= set([n2])
            if desc[n] & desc[n2]:
                return False
            desc[n] |= desc[n2]
    paths = compute_paths(g)
    in_nodes = list(filter(lambda src: g.nodes.data()[src].get('IN'), g.nodes))
    out_nodes = set(filter(lambda src: g.nodes.data()[src].get('OUT'), g.nodes))
    for n in in_nodes:
        if desc[n] & out_nodes:
            return False
    return True

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
