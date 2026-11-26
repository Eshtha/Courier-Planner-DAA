"""Phase 3: route approximation over shortest-path distances."""
from itertools import permutations


def route_length(route, dist):
    return sum(dist[a][b] for a, b in zip(route, route[1:]))


def nearest_neighbour(depot, stops, dist):
    """Closed tour: always visit the closest unvisited stop. O(k^2)."""
    unvisited = set(stops) - {depot}
    route = [depot]
    while unvisited:
        here = route[-1]
        nxt = min(unvisited, key=lambda s: (dist[here][s], s))
        route.append(nxt)
        unvisited.remove(nxt)
    if len(route) > 1:
        route.append(depot)
    return route


def two_opt(route, dist):
    """Optional improvement: reverse segments while the tour gets shorter."""
    best = list(route)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                a, b, c, d = best[i - 1], best[i], best[j], best[j + 1]
                if dist[a][c] + dist[b][d] < dist[a][b] + dist[c][d] - 1e-9:
                    best[i:j + 1] = best[i:j + 1][::-1]
                    improved = True
    return best


def brute_force(depot, stops, dist):
    """Exact optimum, O(k!). Only for verifying small cases."""
    others = sorted(set(stops) - {depot})
    if not others:
        return [depot]
    if len(others) > 9:
        raise ValueError("brute force is limited to 9 stops")
    return min(([depot, *p, depot] for p in permutations(others)),
               key=lambda r: route_length(r, dist))
