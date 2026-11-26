"""Phase 2: box filling with 0/1 knapsack."""
SCALE = 10  # DP works in units of 0.1 kg


def knapsack(parcels, capacity_kg):
    """Return (selected parcels, best value, DP table).

    table[i][w] = best value using the first i parcels within w units.
    Time and space: O(n * W).
    """
    if capacity_kg < 0:
        raise ValueError("capacity cannot be negative")
    capacity = int(capacity_kg * SCALE + 1e-6)
    weights = [round(p.weight * SCALE) for p in parcels]
    table = [[0] * (capacity + 1)]
    for p, wt in zip(parcels, weights):
        prev = table[-1]
        row = prev[:]
        for w in range(wt, capacity + 1):
            take = prev[w - wt] + p.value
            if take > row[w]:
                row[w] = take
        table.append(row)

    chosen, w = [], capacity
    for i in range(len(parcels), 0, -1):  # backtrack
        if table[i][w] != table[i - 1][w]:
            chosen.append(parcels[i - 1])
            w -= weights[i - 1]
    chosen.reverse()
    return chosen, table[-1][capacity], table


def greedy_pack(parcels, capacity_kg):
    """Value/weight greedy heuristic, used only for comparison."""
    left = int(capacity_kg * SCALE + 1e-6)
    chosen = []
    for p in sorted(parcels, key=lambda p: p.value / p.weight, reverse=True):
        wt = round(p.weight * SCALE)
        if wt <= left:
            chosen.append(p)
            left -= wt
    return chosen, sum(p.value for p in chosen)
