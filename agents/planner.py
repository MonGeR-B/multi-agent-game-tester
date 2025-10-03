import random
import asyncio
import uuid
from typing import Optional, List, Dict

try:
    from agents.rag import get_retrieval_qa
    _HAS_RAG = True
except Exception:
    _HAS_RAG = False

class PlannerAgent:
    async def generate_tests(
        self,
        target_url: str,
        n: int = 20,
        seed: Optional[int] = None,
        use_rag: bool = False,
    ) -> List[Dict]:
        """
        Generate `n` candidate test cases for `target_url`.
        If use_rag=True and agents.rag is available, retrieve context first (OpenAI + Chroma).
        Returns a list of structured candidate dicts.
        """

        if seed is not None:
            random.seed(seed)


        context_summary = ""
        if use_rag and _HAS_RAG:
            try:
                qa = get_retrieval_qa() 
                context_summary = await asyncio.to_thread(qa.run, f"Summarize relevant info for {target_url} in 2-3 sentences.")
            except Exception as e:
                context_summary = f"[rag_error: {str(e)}]"
        elif use_rag and not _HAS_RAG:
            context_summary = "[rag_not_available]"

        templates = [
            "Enter numbers {seq} quickly to reach target {target}.",
            "Submit sequence {seq} but skip the middle number.",
            "Try reverse order {seq_rev} and check score.",
            "Input single large number {big} and observe response.",
            "Submit repeated digit {repeat} five times."
        ]

        candidates = []
        for i in range(n):
            try:
                base = random.sample(range(1, 50), k=4)
                seq = "-".join(map(str, base))
                seq_rev = "-".join(map(str, reversed(base)))

                # generate structured candidate
                cid = str(uuid.uuid4())
                description = random.choice(templates).format(
                    seq=seq,
                    seq_rev=seq_rev,
                    target=random.randint(10, 200),
                    big=random.randint(1000, 9999),
                    repeat=random.choice([1, 2, 3, 4, 5])
                )

                if context_summary:
                    description = f"{context_summary}\n\n{description}"

                candidate = {
                    "id": cid,
                    "title": f"Sequence input test #{i+1}",
                    "description": description,
                    "steps": [
                        {"action": "load", "url": target_url},
                        {"action": "fill", "selector": "#input", "value": seq},
                        {"action": "click", "selector": "#submit"}
                    ],
                    "expected": "Game accepts input and updates score/level appropriately",
                    "tags": ["input", "sequence", "edge" if random.random() < 0.2 else "normal"],
                    "estimated_cost": round(random.uniform(0.1, 2.0), 3)
                }

                candidates.append(candidate)

            except Exception as e:
                candidates.append({
                    "id": str(uuid.uuid4()),
                    "title": "generation_error",
                    "description": f"failed to generate candidate #{i+1}: {e}",
                    "steps": [],
                    "expected": "",
                    "tags": ["error"],
                    "estimated_cost": 0.0
                })
            await asyncio.sleep(0)

        return candidates
