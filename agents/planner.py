import random
import asyncio
from typing import Optional

class PlannerAgent:
    async def generate_tests(self, target_url: str, n: int = 20, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        templates = [
            "Enter numbers {seq} quickly to reach target {target}.",
            "Submit sequence {seq} but skip the middle number.",
            "Try reverse order {seq_rev} and check score.",
            "Input single large number {big} and observe response.",
            "Submit repeated digit {repeat} five times."
        ]
        candidates = []
        for i in range(n):
            base = random.sample(range(1, 50), k=4)
            seq = "-".join(map(str, base))
            seq_rev = "-".join(map(str,reversed(base)))
            candidate = {
                "id": f"t{i+1}",
                "description": random.choice(templates).format(
                    seq=seq, seq_rev=seq_rev, target=random.randint(10,200),
                    big=random.randint(1000,9999), repeat=random.choice([1,2,3,4,5])
                ),
                "steps": [
                    {"action": "load", "url": target_url},
                    {"action": "fill", "selector": "#input", "value": seq},
                    {"action": "click", "selector": "#submit"}
                ],
                "estimated_cost": round(random.uniform(0.1, 2.0),3)
            }
            candidates.append(candidate)
            await asyncio.sleep(0)
        return candidates