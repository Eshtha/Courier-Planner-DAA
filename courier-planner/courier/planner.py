"""Integration pipeline: sort -> knapsack -> Dijkstra -> TSP."""
from time import perf_counter

from .graph import dijkstra, path_to
from .knapsack import greedy_pack, knapsack
from .sorting import merge_sort
from .tsp import nearest_neighbour, route_length, two_opt

START_TIME = 9 * 60      # 09:00
SPEED_KMPH = 25
SERVICE_MIN = 3          # handover time per stop


def plan_trip(parcels, depot, graph, capacity, start=START_TIME):
    timings = {}

    t = perf_counter()
    ordered = merge_sort(parcels)
    timings["Sorting"] = perf_counter() - t

    # Reject bad destinations before optimising, so they never take box space.
    t = perf_counter()
    depot_dist, depot_parent = dijkstra(graph, depot)
    reachable, rejected = [], []
    for p in ordered:
        ok = p.destination in graph and depot_dist[p.destination] < float("inf")
        (reachable if ok else rejected).append(p)
    check_time = perf_counter() - t

    t = perf_counter()
    selected, value, table = knapsack(reachable, capacity)
    timings["Knapsack DP"] = perf_counter() - t

    t = perf_counter()
    stops = sorted({p.destination for p in selected} - {depot})
    runs = {depot: (depot_dist, depot_parent)}
    for s in stops:
        runs[s] = dijkstra(graph, s)
    dist = {s: runs[s][0] for s in runs}
    timings["Dijkstra"] = check_time + perf_counter() - t

    t = perf_counter()
    nn_route = nearest_neighbour(depot, stops, dist)
    timings["Nearest neighbour"] = perf_counter() - t

    t = perf_counter()
    better = two_opt(nn_route, dist)
    timings["2-opt"] = perf_counter() - t

    # Expand each leg into the actual roads used, and estimate arrival times.
    legs, clock, total = [], start, 0.0
    arrivals = {depot: start}
    for a, b in zip(better, better[1:]):
        km = dist[a][b]
        total += km
        clock += km / SPEED_KMPH * 60
        legs.append((a, b, km, total, clock, path_to(runs[a][1], b)))
        arrivals.setdefault(b, clock)
        clock += SERVICE_MIN
    deliveries = [(p, arrivals[p.destination]) for p in selected]
    deliveries.sort(key=lambda x: (x[1], x[0].priority, x[0].deadline))

    chosen_ids = {p.pid for p in selected}
    return {
        "sorted": ordered, "selected": selected, "value": value, "table": table,
        "reachable": reachable, "rejected": rejected,
        "deferred": [p for p in reachable if p.pid not in chosen_ids],
        "greedy_value": greedy_pack(reachable, capacity)[1],
        "depot": depot, "stops": stops,
        "shortest": {s: (depot_dist[s], path_to(depot_parent, s)) for s in stops},
        "nn_route": nn_route, "nn_length": route_length(nn_route, dist),
        "route": better, "length": route_length(better, dist),
        "legs": legs, "deliveries": deliveries, "timings": timings,
        "capacity": capacity,
    }
