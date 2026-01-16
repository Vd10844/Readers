from scoring.base import normalize_scores

def select_best_with_confidence(candidates, scoring_fn):
    if not candidates:
        return None

    scores = [scoring_fn(c) for c in candidates]
    confidences = normalize_scores(scores)

    ranked = list(zip(scores, confidences, candidates))
    ranked.sort(key=lambda x: x[0], reverse=True)

    best_score, best_conf, best_candidate = ranked[0]

    return {
        "value": best_candidate.get("value"),
        "page": best_candidate.get("page"),
        "bounding_box": best_candidate.get("bounding_box"),
        "confidence": round(best_conf, 2),
        "rationale": best_candidate.get("rationale")
    }
