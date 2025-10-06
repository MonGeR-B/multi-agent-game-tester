# scripts/compare_candidates.py
import json, difflib, os
A = "reports/initial_candidates.json"
B = "reports/after_candidates.json"
out_md = "reports/compare_initial_after.md"

if not os.path.exists(A) or not os.path.exists(B):
    print("Make sure both files exist:", A, B)
    raise SystemExit(1)

a = json.load(open(A))
b = json.load(open(B))
lines = ["# Candidate comparison — initial vs after\n"]

n = min(len(a), len(b))
for i in range(n):
    ai = a[i]
    bi = b[i]
    lines.append(f"## Test #{i+1}\n")
    lines.append(f"**Initial description:**\n```\n{ai.get('description')}\n```\n")
    lines.append(f"**After (RAG) description:**\n```\n{bi.get('description')}\n```\n")
    # diff
    d = difflib.unified_diff(ai.get('description','').split(), bi.get('description','').split(), lineterm="")
    lines.append("**Diff:**\n```\n" + "\n".join(d) + "\n```\n")
    # show steps count, small note if sleep added
    lines.append(f"- initial steps: {len(ai.get('steps',[]))}, after steps: {len(bi.get('steps',[]))}\n")
    if any(s.get("action")=="sleep" for s in bi.get("steps",[])):
        lines.append("- *Note:* 'sleep' step(s) added in after-candidate (heuristic to avoid race/timeouts)\n")
    lines.append("\n---\n")

open(out_md,"w",encoding="utf-8").write("\n".join(lines))
print("Wrote", out_md)
