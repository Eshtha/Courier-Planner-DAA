# Viva notes

**Intro:** My project plans one courier delivery trip. Merge sort ranks parcels, 0/1 knapsack
chooses which to carry, Dijkstra finds shortest distances, nearest neighbour builds a round
trip and 2-opt improves it. I tested it on three datasets and compared runtimes.

**Flow:** input, validate, sort, reject unreachable, knapsack, Dijkstra, nearest neighbour,
2-opt, arrival times.

- **Why merge sort?** O(n log n) even in the worst case; fastest of my three sorts. It is
  stable, but unique IDs mean stability does not change the order here.
- **Why 0/1 knapsack?** A parcel is taken or left, never split. O(nW), pseudo-polynomial.
- **Recurrence:** dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value), second only if it fits.
- **A cell:** P10 at 15 kg: skip = 241; take = 241 (previous row, 13 kg) + 10 = 251.
- **Find chosen parcels?** Backtrack: if a value differs from the row above, it was taken.
- **Value formula?** (6 - priority) x 10, plus 1 per full hour due before 18:00 (my design choice).
- **Why 151 columns?** 0 to 15 kg in 0.1 kg steps.
- **Why not greedy?** Box 10 kg; (weight, value) A(6,70), B(5,50), C(5,50): greedy by ratio
  gets 70, the best is 100.
- **Dijkstra?** Repeatedly take the closest node from a min-heap and update neighbours.
  O((V+E) log V) per run. Needs non-negative weights. Graph is an adjacency list.
- **Why several runs?** The route needs distances between stops, not only from the depot.
- **TSP?** Shortest tour visiting each stop once and returning; the optimisation is NP-hard.
- **Nearest neighbour?** Go to the closest unvisited stop. O(k^2). Not guaranteed optimal.
- **2-opt?** Reverse a segment if that shortens the tour. Small set: 18.3 to 14.3 km.
- **How tested?** 8 tests: sorted(), exhaustive search, Floyd-Warshall, route and edge checks.
  Tests are evidence, not proof.
- **Why late parcels?** Routing does not enforce deadlines: medium 3, large 37.
- **Priority 1 first?** Not guaranteed. In the small run P06 is delivered before P08.
- **Frontend link?** The page sends dataset and capacity to app.py, which runs the Python
  planner and returns JSON for the page to display.
- **Improvements?** Deadline-aware routing, mandatory urgent parcels, multiple trips, volume.

If you don't know an answer, say what you do understand. Answer honestly about AI help.
