# Task: Redesign the UI of my Courier Planning Dashboard

You are working inside my existing Python project, an algorithms capstone. Improve the
frontend into a polished, professional dashboard. Read the files before changing anything.

## 1. Project overview
The app plans one courier delivery trip:
1. Merge sort orders parcels by priority (1 = most urgent), then deadline, then ID.
2. Unknown or unreachable destinations are rejected.
3. 0/1 knapsack (dynamic programming, 0.1 kg steps) selects the highest-value load.
4. Dijkstra computes shortest paths from the depot and each selected stop.
5. Nearest neighbour builds a round trip; 2-opt improves it.
6. Arrival times are checked against deadlines (09:00 start, 25 km/h, 3 min per stop).

Parcel value = (6 - priority) * 10 + one point per full hour the deadline is before 18:00.

## 2. Structure
- main.py: command line entry point; default capacities small 15, medium 30, large 60 kg
- app.py: Python standard-library web server for the dashboard
- frontend/index.html: dashboard (HTML, CSS, JavaScript). If app.py or frontend/ is
  missing, stop and tell me.
- courier/: models, sorting, knapsack, graph, tsp, planner, report
- data/small, data/medium, data/large: parcels.csv and graph.json
- results/benchmarks/: pipeline_steps.png, sorting.png, knapsack.png, dijkstra.png,
  tsp_runtime.png, served at /charts/<filename>
- tests/test_planner.py: 8 tests
- docs/, screenshots/: report and evidence

Run with `python app.py`, then open http://127.0.0.1:8000.

## 3. API (keep unchanged)
GET /api/plan?dataset=small|medium|large&capacity=0..200
Errors return {"error": "..."} with status 400.

Response fields:
- depot, capacity, load, value, greedy
- sorted: [{id, destination, weight, priority, deadline, value}]
- selected, rejected: arrays of parcel IDs (other parcels are deferred)
- dp: {columns: [whole kg], rows: [[parcelId, [values]]]}
- shortest: [{stop, km, path}]
- nnRoute, nnKm, route, km
- legs: [{from, to, km, total, eta, path}]
- deliveries: [{id, destination, eta, deadline, late}]
- timings: {stepName: milliseconds}
- positions: {node: [x, y]}  (small is a hand-made schematic; y points upward)
- edges: [[nodeA, nodeB, km]]

## 4. Rules
- Change only frontend/ (and the dashboard section of README.md if needed).
- Do not change the algorithms, data, tests, results, or the API.
- All numbers must come from the API. No hardcoded or mock results.
- Use plain HTML, CSS and JavaScript in the single file frontend/index.html. app.py
  does not serve separate CSS or JS files. No frameworks, build step, CDN or external
  fonts: it must work offline.
- Escape text before inserting it with innerHTML.

## 5. UI design
Style: a clean logistics control centre, with clear hierarchy and generous spacing.
- Theme: navy, white and one blue accent. Green means on time, red means late.
  Add a light/dark toggle with readable contrast in both. Wrap any localStorage use
  in try/catch. The benchmark PNGs have white backgrounds, so frame them neatly.
- Layout: a left sidebar on desktop (top navigation on phones) with tabs:
  Overview, Packing, Routing, Performance, About.
- Top bar: dataset selector, capacity input, "Plan delivery" button.
  Changing the dataset resets capacity to its default and reloads.
- Overview: KPI cards (parcels packed, load with a capacity progress bar, total value,
  route length with km and % saved by 2-opt, late parcels), the route map, and a
  pipeline strip showing the six stages. Handle a 0 km route without dividing by zero.
- Packing: sorted parcel table with search, a Packed/Deferred/Rejected filter and
  status badges. Show the DP table with sticky headers and first column, scrolling
  inside its card. Highlight the final best value and the packed parcels' rows.
  Show DP versus greedy value.
- Routing: large SVG map, shortest paths, route legs and delivery schedule.
  - Toggle between the nearest-neighbour order and the 2-opt order. The API gives road
    paths only for the final route (legs). For nearest neighbour, draw dashed lines
    in stop order and label them "stop order, not roads".
  - Play / Pause / Reset animation of the final route, following legs[].path.
    Highlight the current leg and show its ETA.
  - Zoom, pan, reset view, tooltips, and a legend. On the large map, avoid label
    clutter. Say that the small map is a schematic, not to scale.
- Performance: live runtime bars labelled "single run on this computer", then the
  benchmark charts labelled "saved results; not updated by planning". Click to enlarge.
- About: short explanation of each algorithm with its time complexity:
  merge sort O(n log n); knapsack O(nW); Dijkstra O((V+E) log V) per run;
  nearest neighbour O(k^2); 2-opt O(k^2) per pass.
  State that the route is approximate and does not enforce deadlines.

## 6. Quality
- Loading, error and empty states (for example, capacity 0). Disable the button while
  loading, and do not let an older response overwrite a newer one.
- Responsive at 1280 px and 390 px with no page-wide horizontal scroll.
- Keyboard accessible, visible focus, labelled controls. Status must not rely on
  colour alone. Respect prefers-reduced-motion.
- Stay responsive with 500 parcels and 300 graph nodes.

## 7. Check your work
Run `python -m unittest discover -s tests -t . -v` (expect 8 passing), then run the app.
Check these default results:

| Dataset | Packed | Load (kg) | Value | Route (km) | Late |
|---|---|---|---|---|---|
| small, 15 kg | 6 of 10 | 14.5 | 251 | 14.3 | 0 |
| medium, 30 kg | 16 of 60 | 29.9 | 674 | 102.1 | 3 |
| large, 60 kg | 57 of 500 | 60 | 2454 | 231.5 | 37 |

Small at 10 kg: 4 packed, 8.5 kg, value 195, 14.3 km.
Small at 0 kg: nothing packed, 0 km, no errors.
Check every tab, both themes, and the browser console.

## 8. How to work
First give me a short plan, then make the changes. Afterwards, list what changed and
which checks you actually ran. Tell me plainly about anything you could not verify.
