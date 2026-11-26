"""Command-line entry point.  Example: python main.py --dataset small"""
import argparse
from pathlib import Path

from courier.models import load_graph, load_parcels
from courier.planner import plan_trip
from courier.report import format_report, save_outputs

ROOT = Path(__file__).parent
CAPACITY = {"small": 15, "medium": 30, "large": 60}


def main():
    ap = argparse.ArgumentParser(description="Intelligent courier planning system")
    ap.add_argument("--dataset", choices=CAPACITY, default="small")
    ap.add_argument("--capacity", type=float, help="box capacity in kg")
    args = ap.parse_args()
    folder = ROOT / "data" / args.dataset
    capacity = CAPACITY[args.dataset] if args.capacity is None else args.capacity
    try:
        parcels = load_parcels(folder / "parcels.csv")
        depot, graph = load_graph(folder / "graph.json")
        result = plan_trip(parcels, depot, graph, capacity)
    except (OSError, ValueError, KeyError) as e:
        raise SystemExit(f"Error: {e}")
    print(format_report(result))
    out = ROOT / "results" / args.dataset
    save_outputs(result, out)
    print(f"Saved output_trace.txt and dp_table.csv to {out}")


if __name__ == "__main__":
    main()
