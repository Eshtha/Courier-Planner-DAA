"""Creates the sample datasets. Fixed seeds make them reproducible."""
import csv
import json
import math
import random
from pathlib import Path

from courier.models import to_clock

ROOT = Path(__file__).parent / "data"


def random_instance(n_parcels, n_nodes, seed):
    """Connected random road network on a 20 km x 20 km map."""
    rng = random.Random(seed)
    nodes = ["Depot"] + [f"C{i:03d}" for i in range(1, n_nodes)]
    pos = {n: (rng.uniform(0, 20), rng.uniform(0, 20)) for n in nodes}
    edges = {}

    def connect(a, b):
        road = math.dist(pos[a], pos[b]) * rng.uniform(1.05, 1.35)
        edges.setdefault(tuple(sorted((a, b))), max(0.1, round(road, 1)))

    for i in range(1, n_nodes):  # spanning tree guarantees connectivity
        connect(nodes[i], min(nodes[:i], key=lambda m: math.dist(pos[nodes[i]], pos[m])))
    for a in nodes:              # extra roads to 3 nearest neighbours
        for b in sorted(nodes, key=lambda m: math.dist(pos[a], pos[m]))[1:4]:
            connect(a, b)
    parcels = [(f"P{i:04d}", rng.choice(nodes[1:]), rng.randint(5, 80) / 10,
                rng.randint(1, 5), to_clock(rng.randrange(10 * 60, 18 * 60 + 1, 15)))
               for i in range(1, n_parcels + 1)]
    graph = {"depot": "Depot", "nodes": nodes,
             "edges": [[a, b, d] for (a, b), d in edges.items()]}
    return parcels, graph


SMALL_PARCELS = [
    ("P01", "Market", 4.0, 2, "12:00"), ("P02", "Hospital", 2.5, 1, "10:30"),
    ("P03", "College", 6.0, 3, "15:00"), ("P04", "Station", 3.5, 2, "11:30"),
    ("P05", "TechPark", 5.0, 4, "17:00"), ("P06", "Library", 1.5, 3, "14:00"),
    ("P07", "Mall", 7.0, 5, "18:00"), ("P08", "Hospital", 1.0, 1, "10:00"),
    ("P09", "Airport", 8.0, 4, "16:00"), ("P10", "Market", 2.0, 5, "17:30"),
]
SMALL_GRAPH = {
    "depot": "Depot",
    "nodes": ["Depot", "Market", "Hospital", "College", "Station",
              "TechPark", "Library", "Mall", "Airport"],
    "edges": [["Depot", "Market", 2.0], ["Depot", "Station", 4.5],
              ["Depot", "Library", 3.0], ["Market", "Hospital", 1.8],
              ["Market", "Station", 2.0], ["Hospital", "College", 3.2],
              ["Station", "College", 2.5], ["Station", "TechPark", 5.0],
              ["College", "TechPark", 2.2], ["Library", "Mall", 2.7],
              ["Library", "Hospital", 3.5], ["Mall", "Airport", 6.0],
              ["TechPark", "Airport", 4.0], ["Mall", "College", 4.8]],
}


def write(name, parcels, graph):
    folder = ROOT / name
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "parcels.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "destination", "weight_kg", "priority", "deadline"])
        w.writerows(parcels)
    (folder / "graph.json").write_text(json.dumps(graph, indent=1), encoding="utf-8")


if __name__ == "__main__":
    write("small", SMALL_PARCELS, SMALL_GRAPH)
    write("medium", *random_instance(60, 40, seed=7))
    write("large", *random_instance(500, 300, seed=11))
    print("Datasets written to", ROOT)
