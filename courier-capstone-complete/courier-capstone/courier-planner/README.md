# Intelligent Courier Planning System

Capstone project: parcel sorting, 0/1 knapsack packing, Dijkstra shortest paths and
nearest-neighbour TSP approximation (with 2-opt) in one Python application.

## Requirements
Python 3.9 or later. The planner and tests use only the standard library.
`matplotlib` is needed for the charts.

## Execution steps
Open a terminal in this folder. On macOS/Linux, use `python3` if `python` is not found.
```bash
python -m pip install -r requirements.txt
python main.py --dataset small
python main.py --dataset medium
python main.py --dataset large
python main.py --dataset small --capacity 10
python -m unittest discover -s tests -t . -v
python benchmark.py
```
Datasets are included. `python generate_data.py` recreates them.
A run overwrites `results/<dataset>/`, including runs with a custom capacity.
`benchmark.py` overwrites `results/benchmarks/` with timings from your machine.

## Structure
| Path | Contents |
|---|---|
| `courier/` | models, sorting, knapsack, graph, tsp, planner, report |
| `data/` | small, medium and large datasets |
| `tests/` | correctness tests |
| `results/` | output traces, DP tables, benchmark CSVs and charts |
| `docs/` | [design](docs/DESIGN.md) and [final report](docs/REPORT.md) |
| `screenshots/` | screenshots of program runs |

## Phase map
| Phase | Evidence |
|---|---|
| 1 Design | `docs/DESIGN.md` |
| 2 Sorting and packing | `courier/sorting.py`, `courier/knapsack.py`, report section 2 |
| 3 Routing | `courier/graph.py`, `courier/tsp.py`, report section 3 |
| 4 Performance | `benchmark.py`, `tests/`, report section 4 |
| 5 Report and demo | `docs/REPORT.md`, `screenshots/` |

## Web dashboard
```bash
python app.py
```
Open http://127.0.0.1:8000 and keep the terminal running. Press Ctrl+C to stop.
`app.py` calls the Python planner; `frontend/index.html` displays the results.
