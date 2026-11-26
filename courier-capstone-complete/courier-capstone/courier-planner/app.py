"""Web dashboard server. Run: python app.py  then open http://127.0.0.1:8000"""
import json
import math
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from courier.models import load_graph, load_parcels, to_clock
from courier.planner import plan_trip
from main import CAPACITY

ROOT = Path(__file__).parent
SEEDS = {"medium": 7, "large": 11}  # same seeds as generate_data.py
SMALL_LAYOUT = {  # schematic positions for drawing only (not to scale)
    "Depot": (1, 5), "Market": (4, 6.5), "Hospital": (7, 8.5), "Station": (7, 5),
    "Library": (3, 2.5), "Mall": (7, 1), "College": (11, 7), "TechPark": (14, 5),
    "Airport": (13, 1),
}


def layout(name, nodes):
    if name == "small":
        return SMALL_LAYOUT
    rng = random.Random(SEEDS[name])  # reproduces the generator's coordinates
    return {n: (rng.uniform(0, 20), rng.uniform(0, 20)) for n in nodes}


def parcel_json(p):
    return {"id": p.pid, "destination": p.destination, "weight": p.weight,
            "priority": p.priority, "deadline": to_clock(p.deadline), "value": p.value}


def build_plan(name, capacity):
    folder = ROOT / "data" / name
    depot, graph = load_graph(folder / "graph.json")
    r = plan_trip(load_parcels(folder / "parcels.csv"), depot, graph, capacity)
    columns = range(0, len(r["table"][0]), 10)  # whole-kg columns
    labels = ["-"] + [p.pid for p in r["reachable"]]
    return {
        "depot": depot, "capacity": capacity,
        "sorted": [parcel_json(p) for p in r["sorted"]],
        "selected": [p.pid for p in r["selected"]],
        "rejected": [p.pid for p in r["rejected"]],
        "load": round(sum(p.weight for p in r["selected"]), 1),
        "value": r["value"], "greedy": r["greedy_value"],
        "dp": {"columns": [c // 10 for c in columns],
               "rows": [[label, [row[c] for c in columns]]
                        for label, row in zip(labels, r["table"])]},
        "shortest": [{"stop": s, "km": round(km, 1), "path": path}
                     for s, (km, path) in r["shortest"].items()],
        "nnRoute": r["nn_route"], "nnKm": round(r["nn_length"], 1),
        "route": r["route"], "km": round(r["length"], 1),
        "legs": [{"from": a, "to": b, "km": round(km, 1), "total": round(total, 1),
                  "eta": to_clock(eta), "path": path}
                 for a, b, km, total, eta, path in r["legs"]],
        "deliveries": [{"id": p.pid, "destination": p.destination, "eta": to_clock(eta),
                        "deadline": to_clock(p.deadline), "late": eta > p.deadline}
                       for p, eta in r["deliveries"]],
        "timings": {k: v * 1000 for k, v in r["timings"].items()},
        "positions": layout(name, list(graph)),
        "edges": [[u, v, km] for u in graph for v, km in graph[u].items() if u < v],
    }


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, kind):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, data):
        self.send(status, json.dumps(data).encode(), "application/json")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            page = (ROOT / "frontend" / "index.html").read_bytes()
            return self.send(200, page, "text/html; charset=utf-8")
        if url.path == "/api/plan":
            query = parse_qs(url.query)
            name = query.get("dataset", ["small"])[0]
            try:
                if name not in CAPACITY:
                    raise ValueError("unknown dataset")
                capacity = float(query.get("capacity", [CAPACITY[name]])[0])
                if not (math.isfinite(capacity) and 0 <= capacity <= 200):
                    raise ValueError("capacity must be between 0 and 200 kg")
                return self.send_json(200, build_plan(name, capacity))
            except ValueError as error:
                return self.send_json(400, {"error": str(error)})
        charts = {f"/charts/{p.name}": p for p in (ROOT / "results" / "benchmarks").glob("*.png")}
        if url.path in charts:
            return self.send(200, charts[url.path].read_bytes(), "image/png")
        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    print("Dashboard running at http://127.0.0.1:8000  (Ctrl+C to stop)")
    try:
        ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
