"""Readable console output and CSV evidence files."""
import csv
from pathlib import Path

from .models import to_clock


def _title(text):
    return f"\n{'=' * 70}\n{text}\n{'=' * 70}"


def _parcel_rows(parcels):
    rows = [f"{'ID':<7}{'Destination':<14}{'kg':>6}{'Prio':>6}{'Deadline':>10}{'Value':>7}"]
    rows += [f"{p.pid:<7}{p.destination:<14}{p.weight:>6.1f}{p.priority:>6}"
             f"{to_clock(p.deadline):>10}{p.value:>7}" for p in parcels]
    return rows


def format_report(r):
    out = [_title("1. PRIORITISED PARCELS (merge sort: priority, then deadline)")]
    out += _parcel_rows(r["sorted"])
    if r["rejected"]:
        out.append("Rejected (unknown/unreachable destination): "
                   + ", ".join(p.pid for p in r["rejected"]))

    out.append(_title(f"2. PACKING PLAN (0/1 knapsack, capacity {r['capacity']} kg)"))
    out += _parcel_rows(r["selected"])
    load = sum(p.weight for p in r["selected"])
    out.append(f"Loaded weight : {load:.1f} / {r['capacity']} kg")
    out.append(f"DP value      : {r['value']}   (greedy heuristic: {r['greedy_value']})")
    out.append(f"DP table size : {len(r['table'])} rows x {len(r['table'][0])} columns")
    out.append("Deferred      : " + (", ".join(p.pid for p in r["deferred"]) or "none"))
    out.append("\nDP table excerpt (columns are whole kg):")
    cols = range(0, len(r["table"][0]), 10)
    shown = list(cols)
    out.append("item   " + "".join(f"{c // 10:>5}" for c in shown))
    names = ["-"] + [p.pid for p in r["reachable"]]
    for i, row in enumerate(r["table"][:16]):
        out.append(f"{names[i]:<7}" + "".join(f"{row[c]:>5}" for c in shown))
    if len(r["table"]) > 16:
        out.append(f"... ({len(r['table']) - 16} more rows; see dp_table.csv)")

    out.append(_title(f"3. SHORTEST PATHS FROM {r['depot']} (Dijkstra)"))
    for stop, (km, path) in r["shortest"].items():
        out.append(f"{stop:<14}{km:>7.1f} km   {' -> '.join(path)}")

    out.append(_title("4. DELIVERY ROUTE"))
    out.append(f"Nearest neighbour : {' -> '.join(r['nn_route'])}  = {r['nn_length']:.1f} km")
    out.append(f"After 2-opt       : {' -> '.join(r['route'])}  = {r['length']:.1f} km")
    out.append("\nLegs of the final route:")
    for n, (a, b, km, total, eta, path) in enumerate(r["legs"], 1):
        out.append(f"{n:>2}. {a} to {b}: {km:.1f} km (total {total:.1f}), "
                   f"arrive {to_clock(eta)} via {' -> '.join(path)}")

    out.append(_title("5. DELIVERY SCHEDULE (09:00 start, 25 km/h, 3 min per stop)"))
    for p, eta in r["deliveries"]:
        status = "ON TIME" if eta <= p.deadline else "LATE"
        out.append(f"{p.pid:<7}{p.destination:<14}ETA {to_clock(eta)}  "
                   f"due {to_clock(p.deadline)}  {status}")

    out.append(_title("6. RUNTIME OF MAJOR STEPS (single run)"))
    out += [f"{k:<20}{v * 1000:>10.3f} ms" for k, v in r["timings"].items()]
    return "\n".join(out) + "\n"


def save_outputs(r, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "output_trace.txt").write_text(format_report(r), encoding="utf-8")
    with open(folder / "dp_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["parcel"] + [f"{c / 10:.1f}kg" for c in range(len(r["table"][0]))])
        for name, row in zip(["-"] + [p.pid for p in r["reachable"]], r["table"]):
            w.writerow([name] + row)
