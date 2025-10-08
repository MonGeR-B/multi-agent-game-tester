import json
import random
import re
import ast
from typing import Optional, List, cast

from agents.llm_provider import LLMProvider
from agents.rag import get_retriever, generate_answer_with_rag


class PlannerAgent:
    """
    PlannerAgent generates RAG-aware test cases for any target game URL.
    It combines prior run knowledge (via retriever) + an LLM model (OpenAI / Ollama).
    """

    def __init__(self):
        self.provider = LLMProvider()

    def _fallback_candidates(self, target_url: str, n: int) -> List[dict]:
        """If LLM fails, fallback to simple random templates."""
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
            seq_rev = "-".join(map(str, reversed(base)))
            candidate = {
                "id": f"t{i+1}",
                "description": random.choice(templates).format(
                    seq=seq,
                    seq_rev=seq_rev,
                    target=random.randint(10, 200),
                    big=random.randint(1000, 9999),
                    repeat=random.choice([1, 2, 3, 4, 5])
                ),
                "steps": [
                    {"action": "load", "url": target_url},
                    {"action": "fill", "selector": "#input", "value": seq},
                    {"action": "click", "selector": "#submit"}
                ],
                "estimated_cost": round(random.uniform(0.1, 2.0), 3)
            }
            candidates.append(candidate)
        return candidates

    def generate_tests(self, target_url: str, n: int = 20, seed: Optional[int] = None) -> List[dict]:
        """
        Generate n test cases for a target URL using RAG + LLM context.
        Returns a list of structured test case dicts.
        """
        if seed is not None:
            random.seed(seed)

        print(f"[Planner] Generating {n} test cases for: {target_url}")

        # 1️⃣ Retrieve prior context from RAG (knowledge store)
        try:
            retriever = get_retriever()
            print("[Planner] Fetching prior context from vector DB...")
            ctx_summary = generate_answer_with_rag(
                retriever,
                f"Summarize prior run results, failure patterns, and valid interactions for {target_url}",
                k=3,
                temperature=0.0
            )
        except Exception as e:
            print(f"[Planner] RAG retrieval failed / not available: {e}")
            ctx_summary = "No prior context available."

        print("[Planner] Context summary received.")

        # 2️⃣ Build prompt for LLM generation
        prompt = f"""
SYSTEM INSTRUCTION:
You are a test case generation AI. You must output ONLY a valid JSON array — no explanations, no markdown, no bullet points, no comments.
If you cannot format valid JSON, return an empty array [].

CONTEXT (from prior runs and knowledge base):
{ctx_summary}

TASK:
Generate exactly {n} candidate test cases for the web game at: {target_url}.

EACH OBJECT MUST HAVE THIS STRUCTURE:
{{
  "id": "t<number>",
  "description": "Short one-line description of what to test.",
  "steps": [
    {{"action": "load", "url": "{target_url}"}},
    {{"action": "wait", "selector": "any-CSS-selector"}},
    {{"action": "fill", "selector": "#input", "value": "some test data"}},
    {{"action": "click", "selector": "#submit"}}
  ],
  "estimated_cost": <float between 0.2 and 2.5>
}}

Return the entire output as a JSON array of such objects.
"""

        # --- Improved output handling and JSON repair ---
        import ast, json, re

        # Expand token limit (prevents truncation)
        raw = self.provider.generate(
            prompt + "\n\nReturn only a valid JSON array — no extra text.",
            temperature=0.0,
            max_tokens=3000  # increased from 1800
        ).strip()

        # Remove markdown fences and junk
        cleaned = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
        cleaned = re.sub(r',(\s*[\]\}])', r'\1', cleaned)

        # Try parsing the raw output
        try:
            candidates = json.loads(cleaned)
        except Exception as e:
            print(f"[Planner] Initial parse failed: {e}")
            # try to auto-repair truncated JSON
            if cleaned.endswith("}") or cleaned.endswith("]"):
                # looks truncated — try to fix closing bracket
                if cleaned.count("{") > cleaned.count("}"):
                    cleaned += "}" * (cleaned.count("{") - cleaned.count("}"))
                if cleaned.count("[") > cleaned.count("]"):
                    cleaned += "]" * (cleaned.count("[") - cleaned.count("]"))
            # Second attempt
            try:
                candidates = json.loads(cleaned)
                print(f"[Planner] Repaired truncated JSON successfully.")
            except Exception as e2:
                # fallback repair using LLM itself
                print(f"[Planner] JSON still invalid. Attempting repair via LLM...")
                repair_prompt = (
                    "Extract a valid JSON array from the following text. "
                    "If the array seems incomplete, infer the missing closing brackets.\n\n"
                    "TEXT:\n" + cleaned
                )
                repaired = self.provider.generate(repair_prompt, temperature=0.0, max_tokens=800)
                repaired = re.sub(r"^```(?:json)?", "", repaired, flags=re.IGNORECASE).strip()
                repaired = re.sub(r"```$", "", repaired).strip()
                try:
                    candidates = json.loads(repaired)
                    print(f"[Planner] Repair succeeded using LLM.")
                except Exception as e3:
                    print(f"[Planner] Repair failed: {e3}")
                    with open("reports/llm_raw_fail.txt", "w", encoding="utf8") as fh:
                        fh.write(raw)
                    candidates = self._fallback_candidates(target_url, n)
                    print(f"[Planner] Using fallback {len(candidates)} random candidates.")
        # --- End improved parsing block ---

        # 5️⃣ Ensure count
        if not candidates or not isinstance(candidates, list):
            print("[Planner] Falling back to context-aware synthesis or simple fallback.")
            candidates = self._fallback_candidates(target_url, n)

        if len(candidates) < n:
            diff = n - len(candidates)
            print(f"[Planner] Only {len(candidates)} generated; padding {diff} fallback ones.")
            candidates += self._fallback_candidates(target_url, diff)

        print("[Planner] Generation complete.")
        return cast(List[dict], candidates)


# Quick CLI for local testing
if __name__ == "__main__":
    import sys, os
    url = sys.argv[1] if len(sys.argv) > 1 else "https://play.ezygamers.com/"
    planner = PlannerAgent()
    tests = planner.generate_tests(url, n=10, seed=42)
    os.makedirs("reports", exist_ok=True)
    out_path = "reports/after_candidates.json"
    with open(out_path, "w", encoding="utf8") as f:
        json.dump(tests, f, indent=2)
    print(f"[Planner] Saved candidates → {out_path}")
