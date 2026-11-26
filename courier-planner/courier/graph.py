"""Phase 3: Dijkstra's shortest path with a binary heap."""
import heapq


def dijkstra(graph, source):
    """Return (distance, parent) maps. O((V + E) log V)."""
    dist = {node: float("inf") for node in graph}
    parent = {source: None}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue  # stale heap entry
        for v, km in graph[u].items():
            nd = d + km
            if nd < dist[v]:
                dist[v], parent[v] = nd, u
                heapq.heappush(heap, (nd, v))
    return dist, parent


def path_to(parent, target):
    if target not in parent:
        return []
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return path[::-1]
