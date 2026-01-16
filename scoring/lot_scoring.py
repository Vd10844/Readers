from scoring.base import normalize_scores

def score_lot_candidate(candidate: dict) -> int:
    score = 0
    value = candidate.get("value") or ""
    rationale = (candidate.get("rationale") or "").lower()

    if value.isdigit():
        score += 3
        if len(value) <= 3:
            score += 3

    if len(value) > 6:
        score -= 3

    if "optional" in rationale:
        score += 4
    if "misc" in rationale or "reference" in rationale:
        score -= 4

    return score
