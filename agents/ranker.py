class RankerAgent:
    """
    Simple scoring system:
    - Uses estimated_cost as the main score
    - Adds a small bias from the test_id (so it's deterministic)
    - Lower score = better
    """

    def rank_and_select(self, candidates, top_k: int = 10):
        scored = []
        for c in candidates:
            score = c.get("estimated_cost", 1.0)
            bias = (sum(ord(ch) for ch in c["id"]) % 10) / 100.0
            scored.append((score + bias, c))
        scored.sort(key=lambda x: x[0])
        selected = [c for _, c in scored[:top_k]]
        return selected
