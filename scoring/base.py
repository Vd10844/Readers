from typing import List

def normalize_scores(scores: List[int]) -> List[float]:
    if not scores:
        return []
    min_s, max_s = min(scores), max(scores)
    if min_s == max_s:
        return [1.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]
