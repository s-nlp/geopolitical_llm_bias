from typing import List, Tuple


def _normalize(s: str) -> str:

    return " ".join(s.strip().lower().split())


def top_k_similar(query: str, choices: List[str], k: int = 5) -> List[Tuple[str, float]]:

    try:
        from rapidfuzz import fuzz
    except Exception:
        # Fallback to simple ratio
        def simple_ratio(a: str, b: str) -> int:
            set_a = set(a)
            set_b = set(b)
            if not set_a and not set_b:
                return 100
            inter = len(set_a & set_b)
            union = len(set_a | set_b)
            return int(100 * inter / max(1, union))

        def scorer(a: str, b: str) -> int:
            return simple_ratio(a, b)
    else:
        def scorer(a: str, b: str) -> int:  # type: ignore
            return int(fuzz.token_sort_ratio(a, b))

    qn = _normalize(query)
    scored = []
    for c in choices:
        sn = _normalize(c)
        score = scorer(qn, sn)
        scored.append((c, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


