#!/usr/bin/env bash
# Ask Perplexity (web-grounded search). Prints the answer followed by numbered citations.
# Research is CONTEXT ONLY - it never changes RAAM signals or weights.
#
# Usage: perplexity.sh "question" [recency]     recency: day|week|month (optional)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_env.sh"
load_env "$ROOT"

q="${1:?usage: perplexity.sh \"question\" [day|week|month]}"
recency="${2:-}"
if [[ -z "${PERPLEXITY_API_KEY:-}" ]]; then
  echo "perplexity.sh: PERPLEXITY_API_KEY not set - research skipped."
  exit 0
fi

PY="$(command -v python3 || command -v python)"
body="$("$PY" - "$q" "${PERPLEXITY_MODEL:-sonar}" "$recency" <<'EOF'
import json, sys
q, model, recency = sys.argv[1], sys.argv[2], sys.argv[3]
payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a concise financial research assistant. "
         "Answer factually with dates. Say plainly when you find nothing relevant."},
        {"role": "user", "content": q},
    ],
}
if recency:
    payload["search_recency_filter"] = recency
print(json.dumps(payload))
EOF
)"

resp="$(curl -sS -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$body" 2>&1)" || { echo "perplexity.sh: request failed: ${resp:0:300}"; exit 0; }

"$PY" - "$resp" <<'EOF'
import json, sys
try:
    r = json.loads(sys.argv[1])
except Exception:
    print("perplexity.sh: non-JSON response:", sys.argv[1][:300]); sys.exit(0)
if "choices" not in r:
    print("perplexity.sh: error response:", json.dumps(r)[:300]); sys.exit(0)
print(r["choices"][0]["message"]["content"].strip())
cites = r.get("citations") or [s.get("url") for s in r.get("search_results", []) if s.get("url")]
if cites:
    print("\nSources:")
    for i, c in enumerate(cites, 1):
        print(f"[{i}] {c}")
EOF
exit 0
