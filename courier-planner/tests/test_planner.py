import random
import unittest
from itertools import combinations
from pathlib import Path

from courier.graph import dijkstra, path_to
from courier.knapsack import knapsack
from courier.models import Parcel, load_graph, load_parcels
from courier.planner import plan_trip
from courier.sorting import insertion_sort, merge_sort, quick_sort, urgency_key
from courier.tsp import brute_force, nearest_neighbour, route_length, two_opt
from generate_data import random_instance

DATA = Path(__file__).parent.parent / "data"


def random_parcels(n, rng):
    return [Parcel(f"P{i}", "A", rng.randint(1, 60) / 10, rng.randint(1, 5),
                   rng.randint(600, 1080)) for i in range(n)]


class TestSorting(unittest.TestCase):
    def test_all_sorts_match_builtin(self):
        rng = random.Random(1)
        for n in (0, 1, 2, 17, 200):
            items = random_parcels(n, rng)
            expected = sorted(items, key=urgency_key)
            for fn in (merge_sort, quick_sort, insertion_sort):
                self.assertEqual(fn(items), expected)


class TestKnapsack(unittest.TestCase):
    def test_matches_exhaustive_search(self):
        rng = random.Random(2)
        for _ in range(100):
            items = random_parcels(rng.randint(0, 9), rng)
            cap = rng.randint(0, 150) / 10
            best = max(sum(p.value for p in c)
                       for k in range(len(items) + 1)
                       for c in combinations(items, k)
                       if sum(round(p.weight * 10) for p in c) <= round(cap * 10))
            chosen, value, _ = knapsack(items, cap)
            self.assertEqual(value, best)
            self.assertEqual(value, sum(p.value for p in chosen))
            self.assertLessEqual(sum(p.weight for p in chosen), cap + 1e-6)


class TestDijkstra(unittest.TestCase):
    def test_matches_floyd_warshall(self):
        for seed in range(10):
            _, data = random_instance(1, 20, seed)
            nodes = data["nodes"]
            graph = {n: {} for n in nodes}
            for a, b, d in data["edges"]:
                graph[a][b] = graph[b][a] = d
            fw = {a: {b: 0 if a == b else graph[a].get(b, float("inf"))
                      for b in nodes} for a in nodes}
            for k in nodes:
                for i in nodes:
                    for j in nodes:
                        fw[i][j] = min(fw[i][j], fw[i][k] + fw[k][j])
            for s in nodes:
                dist, parent = dijkstra(graph, s)
                for t in nodes:
                    self.assertAlmostEqual(dist[t], fw[s][t])
                    path = path_to(parent, t)
                    self.assertAlmostEqual(
                        sum(graph[a][b] for a, b in zip(path, path[1:])), dist[t])

    def test_unreachable(self):
        dist, parent = dijkstra({"A": {}, "B": {}}, "A")
        self.assertEqual(dist["B"], float("inf"))
        self.assertEqual(path_to(parent, "B"), [])


class TestRouting(unittest.TestCase):
    def test_routes_are_valid_and_bounded_by_optimum(self):
        for seed in range(15):
            _, data = random_instance(1, 8, seed)
            graph = {n: {} for n in data["nodes"]}
            for a, b, d in data["edges"]:
                graph[a][b] = graph[b][a] = d
            dist = {n: dijkstra(graph, n)[0] for n in graph}
            nn = nearest_neighbour("Depot", list(graph), dist)
            improved = two_opt(nn, dist)
            optimum = route_length(brute_force("Depot", list(graph), dist), dist)
            for r in (nn, improved):
                self.assertEqual(sorted(r[:-1]), sorted(graph))
                self.assertEqual(r[0], r[-1])
            self.assertLessEqual(route_length(improved, dist), route_length(nn, dist) + 1e-9)
            self.assertGreaterEqual(route_length(improved, dist), optimum - 1e-9)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.parcels = load_parcels(DATA / "small" / "parcels.csv")
        self.depot, self.graph = load_graph(DATA / "small" / "graph.json")

    def test_end_to_end(self):
        r = plan_trip(self.parcels, self.depot, self.graph, 15)
        self.assertLessEqual(sum(p.weight for p in r["selected"]), 15)
        self.assertEqual(set(r["route"][1:-1]), {p.destination for p in r["selected"]})
        self.assertEqual(len(r["deliveries"]), len(r["selected"]))

    def test_zero_capacity(self):
        r = plan_trip(self.parcels, self.depot, self.graph, 0)
        self.assertEqual((r["selected"], r["route"], r["length"]), ([], ["Depot"], 0))

    def test_unknown_destination_rejected(self):
        bad = Parcel("X1", "Nowhere", 1.0, 1, 600)
        r = plan_trip(self.parcels + [bad], self.depot, self.graph, 15)
        self.assertEqual(r["rejected"], [bad])
        self.assertNotIn(bad, r["selected"])


if __name__ == "__main__":
    unittest.main()
