from heapq import heappush, heappop
import networkx as nx


def k_shortest_paths(G, source, target, K=1, weight='weight'):
    """Returns the K-shortest paths from source to target in a weighted graph G.
    Parameters
    ----------
    G : NetworkX graph
    source : node
       Starting node
    target : node
       Ending node

    K : integer, optional (default=1)
        The number of shortest paths to find
    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight
    Returns
    -------
    lengths, paths : lists
       Returns a tuple with two lists.
       The first list stores the length of each k-shortest path.
       The second list stores each k-shortest path.
    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.
    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print(k_shortest_paths(G, 0, 4, 4))
    ([1, 2, 2, 2], [[0, 4], [0, 1, 4], [0, 2, 4], [0, 3, 4]])
    Notes
    ------
    Edge weight attributes must be numerical and non-negative.
    Distances are calculated as sums of weighted edges traversed.
    """
    if source == target:
        return ([0], [[source]])

    length, path = nx.single_source_dijkstra(G, source, target, weight=weight)
    if target not in path:
        raise nx.NetworkXNoPath("node %s not reachable from %s" % (source, target))

    # save path as (vertex array, spur index)
    lengths = [length]
    paths = [(path, 0)]
    # c = count()
    B = []

    for k in range(1, K):
        G_original = G.copy()
        prev_spur = paths[k-1][1]
        # remove from G all the vertices in the root path before the spur node
        root_path = paths[-1][0][0:prev_spur]
        G.remove_nodes_from(root_path)
        # root_path_len = get_path_length(G, root_path, weight)

        # note sure about this one
        for (path, _) in paths[:-1]:
            if path[0:prev_spur] == root_path:
                G.remove_edge(path[prev_spur], path[prev_spur + 1])

        for i in range(prev_spur, len(paths[-1][0]) - 1):
            spur_node = paths[-1][0][i]

            # remove the edge coming out of the spur node in the A[k-1] path
            G.remove_edge(paths[-1][0][i], paths[-1][0][i+1])

            try:
                spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, target, weight=weight)
            except nx.NetworkXNoPath:
                break
            if target in spur_path:
                total_path = root_path + spur_path
                total_path_length = get_path_length(G_original, total_path, weight)
                heappush(B, (total_path_length, (total_path, i)))

            root_path.append(paths[-1][0][i])
            # root_path_len += G.get_edge_data(root_path[i-1], root_path[i])[weight]

        G = G_original

        if B:
            (l, p) = heappop(B)
            lengths.append(l)
            paths.append(p)
        else:
            break

    return lengths, [path[0] for path in paths]


def get_path_length(G, path, weight='weight'):
    length = 0
    if len(path) > 1:
        for i in range(len(path) - 1):
            length += G.get_edge_data(path[i], path[i+1])[weight]

    return length


if __name__ == "__main__":
     G = nx.DiGraph()
     G.add_edge('C', 'D', length=3, weight=1)
     G.add_edge('C', 'E', length=2, weight=2)
     G.add_edge('D', 'F', length=4, weight=3)
     G.add_edge('E', 'D', length=1, weight=4)
     G.add_edge('E', 'F', length=2, weight=5)
     G.add_edge('E', 'G', length=3, weight=6)
     G.add_edge('F', 'G', length=2, weight=7)
     G.add_edge('F', 'H', length=1, weight=8)
     G.add_edge('G', 'H', length=2, weight=9)

     for e in G.edges:
         print (e)

     print(k_shortest_paths(G, 'C', 'H', 3, "length"))
