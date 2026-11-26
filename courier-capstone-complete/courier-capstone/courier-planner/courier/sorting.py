"""Phase 2: parcel prioritisation."""


def urgency_key(p):
    return (p.priority, p.deadline, p.pid)


def merge_sort(items, key=urgency_key):
    """Stable, O(n log n) in every case. Used by the planner."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left, right = merge_sort(items[:mid], key), merge_sort(items[mid:], key)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(right[j]) < key(left[i]):
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    return out + left[i:] + right[j:]


def quick_sort(items, key=urgency_key):
    """Middle-pivot, three-way quick sort (comparison baseline)."""
    if len(items) <= 1:
        return list(items)
    pivot = key(items[len(items) // 2])
    less = [x for x in items if key(x) < pivot]
    same = [x for x in items if key(x) == pivot]
    more = [x for x in items if key(x) > pivot]
    return quick_sort(less, key) + same + quick_sort(more, key)


def insertion_sort(items, key=urgency_key):
    """O(n^2) comparison baseline."""
    out = list(items)
    for i in range(1, len(out)):
        current, k, j = out[i], key(out[i]), i - 1
        while j >= 0 and key(out[j]) > k:
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = current
    return out
