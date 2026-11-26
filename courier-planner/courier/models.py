"""Data models, input loading and validation."""
import csv
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Parcel:
    pid: str
    destination: str
    weight: float   # kg, at most one decimal place
    priority: int   # 1 (most urgent) .. 5 (least urgent)
    deadline: int   # minutes after midnight

    @property
    def value(self):
        """Knapsack benefit: priority dominates, early deadlines add a bonus."""
        bonus = max(0, (18 * 60 - self.deadline) // 60)  # per hour before 18:00
        return (6 - self.priority) * 10 + bonus


def to_minutes(text):
    hours, minutes = map(int, text.split(":"))
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ValueError(f"invalid time: {text}")
    return hours * 60 + minutes


def to_clock(minutes):
    return f"{int(minutes) // 60:02d}:{int(minutes) % 60:02d}"


def load_parcels(path):
    parcels, seen = [], set()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = Parcel(row["id"], row["destination"], float(row["weight_kg"]),
                       int(row["priority"]), to_minutes(row["deadline"]))
            if p.pid in seen:
                raise ValueError(f"duplicate parcel id: {p.pid}")
            if p.weight <= 0 or abs(p.weight * 10 - round(p.weight * 10)) > 1e-6:
                raise ValueError(f"{p.pid}: weight must be positive, in 0.1 kg steps")
            if not 1 <= p.priority <= 5:
                raise ValueError(f"{p.pid}: priority must be 1..5")
            seen.add(p.pid)
            parcels.append(p)
    return parcels


def load_graph(path):
    """Return (depot, adjacency list) for an undirected weighted road graph."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    graph = {node: {} for node in data["nodes"]}
    for u, v, km in data["edges"]:
        if u not in graph or v not in graph:
            raise ValueError(f"edge uses unknown node: {u}-{v}")
        if km < 0:
            raise ValueError("Dijkstra requires non-negative distances")
        best = min(km, graph[u].get(v, km))
        graph[u][v] = graph[v][u] = best
    if data["depot"] not in graph:
        raise ValueError("depot is not a graph node")
    return data["depot"], graph
