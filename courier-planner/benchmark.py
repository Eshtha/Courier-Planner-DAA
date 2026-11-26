"""Phase 4: runtime measurements and charts.  Run: python benchmark.py"""
import csv
import platform
import random
import statistics
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from courier.graph import dijkstra
from courier.knapsack import knapsack
from courier.models import Parcel, load_graph, load_parcels, to_minutes
from courier.planner import plan_trip
from courier.sorting import insertion_sort, merge_sort, quick_sort
from courier.tsp import brute_force, nearest_neighbour, route_length, two_opt
from generate_data import random_instance

ROOT = Path(__file__).parent
OUT = ROOT / "results" / "benchmarks"
REPEATS = 5


def timed(fn):
    """Median of several runs, in milliseconds."""
    samples = []
    for _ in range(REPEATS):
        t = perf_counter()
        fn()
        samples.append((perf_counter() - t) * 1000)
    return statistics.median(samples)


def save_csv(name, header, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"\n{name}\n" + " | ".join(header))
    for row in rows:
        print(" | ".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in row))


def line_chart(filename, title, xlabel, xs, series, ylabel="Median runtime (ms)", log=True):
    plt.figure(figsize=(8, 5))
    for (label, ys), marker in zip(series.items(), "os^d"):
        plt.plot(xs, ys, marker=marker, label=label)
    if log:
        plt.yscale("log")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel + (" - log scale" if log else ""))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=150)
    plt.close()


def bench_pipeline():
    rows, steps = [], None
    names = {"small": 15, "medium": 30, "large": 60}
    for name, cap in names.items():
        parcels = load_parcels(ROOT / "data" / name / "parcels.csv")
        depot, graph = load_graph(ROOT / "data" / name / "graph.json")
        runs = [plan_trip(parcels, depot, graph, cap) for _ in range(REPEATS)]
        steps = list(runs[0]["timings"])
        med = [statistics.median(r["timings"][s] for r in runs) * 1000 for s in steps]
        r = runs[0]
        rows.append([name, len(parcels), len(graph), len(r["selected"]), len(r["stops"]),
                     *med, r["nn_length"], r["length"],
                     r["value"], r["greedy_value"],
                     sum(eta > p.deadline for p, eta in r["deliveries"])])
    save_csv("pipeline.csv", ["dataset", "parcels", "nodes", "selected", "stops",
             *[f"{s} ms" for s in steps], "nn_km", "2opt_km", "dp_value",
             "greedy_value", "late"], rows)
    plt.figure(figsize=(9, 5))
    width = 0.26
    for i, row in enumerate(rows):
        plt.bar([x + (i - 1) * width for x in range(len(steps))],
                row[5:5 + len(steps)], width, label=row[0])
    plt.xticks(range(len(steps)), steps)
    plt.yscale("log")
    plt.ylabel("Median runtime (ms) - log scale")
    plt.title("Runtime of major pipeline steps")
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "pipeline_steps.png", dpi=150)
    plt.close()


def bench_sorting():
    rng = random.Random(3)
    sizes = [100, 500, 1000, 2000, 5000]
    algos = {"Merge sort": merge_sort, "Quick sort": quick_sort,
             "Insertion sort": insertion_sort}
    series = {k: [] for k in algos}
    for n in sizes:
        items = [Parcel(f"P{i:05d}", "A", 1.0, rng.randint(1, 5),
                        rng.randint(to_minutes("10:00"), to_minutes("18:00")))
                 for i in range(n)]
        for label, fn in algos.items():
            series[label].append(timed(lambda: fn(items)))
    save_csv("sorting.csv", ["n", *algos],
             [[n, *[series[a][i] for a in algos]] for i, n in enumerate(sizes)])
    line_chart("sorting.png", "Sorting algorithm comparison", "Parcels (n)", sizes, series)


def bench_dijkstra():
    sizes, times = [50, 100, 500, 1000, 3000], []
    for n in sizes:
        _, data = random_instance(1, n, seed=n)
        graph = {v: {} for v in data["nodes"]}
        for a, b, d in data["edges"]:
            graph[a][b] = graph[b][a] = d
        times.append(timed(lambda: dijkstra(graph, "Depot")))
    save_csv("dijkstra.csv", ["nodes", "ms"], [list(x) for x in zip(sizes, times)])
    line_chart("dijkstra.png", "Dijkstra (single source) scaling", "Graph nodes",
               sizes, {"Dijkstra": times}, log=False)


def bench_tsp():
    """Route quality and speed against the exact optimum, averaged over 10 maps."""
    sizes = [4, 5, 6, 7, 8, 9]
    rows = []
    for k in sizes:
        t = {"nn": [], "opt": [], "bf": []}
        gap_nn, gap_2 = [], []
        for seed in range(10):
            _, data = random_instance(1, k + 1, seed=100 + seed)
            graph = {v: {} for v in data["nodes"]}
            for a, b, d in data["edges"]:
                graph[a][b] = graph[b][a] = d
            dist = {v: dijkstra(graph, v)[0] for v in graph}
            stops = list(graph)
            nn = nearest_neighbour("Depot", stops, dist)
            best = route_length(brute_force("Depot", stops, dist), dist)
            gap_nn.append((route_length(nn, dist) / best - 1) * 100)
            gap_2.append((route_length(two_opt(nn, dist), dist) / best - 1) * 100)
            t["nn"].append(timed(lambda: nearest_neighbour("Depot", stops, dist)))
            t["opt"].append(timed(lambda: two_opt(nearest_neighbour("Depot", stops, dist), dist)))
            t["bf"].append(timed(lambda: brute_force("Depot", stops, dist)))
        rows.append([k, *(statistics.mean(t[x]) for x in ("nn", "opt", "bf")),
                     statistics.mean(gap_nn), statistics.mean(gap_2)])
    save_csv("tsp.csv", ["stops", "nn_ms", "nn_2opt_ms", "bruteforce_ms",
                         "nn_gap_pct", "2opt_gap_pct"], rows)
    line_chart("tsp_runtime.png", "TSP: approximation vs exact search", "Delivery stops", sizes,
               {"Nearest neighbour": [r[1] for r in rows],
                "NN + 2-opt": [r[2] for r in rows],
                "Brute force": [r[3] for r in rows]})


def bench_knapsack():
    rng = random.Random(5)
    sizes, times = [50, 100, 200, 500, 1000], []
    for n in sizes:
        items = [Parcel(f"P{i}", "A", rng.randint(5, 80) / 10, rng.randint(1, 5), 720)
                 for i in range(n)]
        times.append(timed(lambda: knapsack(items, 60)))
    save_csv("knapsack.csv", ["n (capacity 60 kg)", "ms"], [list(x) for x in zip(sizes, times)])
    line_chart("knapsack.png", "0/1 knapsack scaling (capacity 60 kg)", "Parcels (n)",
               sizes, {"DP": times}, log=False)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Python {platform.python_version()} on {platform.system()}; median of {REPEATS} runs")
    bench_pipeline()
    bench_sorting()
    bench_knapsack()
    bench_dijkstra()
    bench_tsp()
    print(f"\nCharts and CSV files saved in {OUT}")
