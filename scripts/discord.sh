#!/usr/bin/env bash
# Post a message (optionally with one file attachment) to the RAAM Discord channel via webhook.
# Never fails the caller: notification problems must not block trading.
#
# Usage: discord.sh "message text"                (or pipe text on stdin)
#        discord.sh --file reports/2026-10.pdf "message text"
# Needs env var DISCORD_WEBHOOK_URL (cloud environment variable; local .env for testing).
# If it is unset, the message (and file path) is printed to stdout instead.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_env.sh"
load_env "$ROOT"

file=""
if [[ "${1:-}" == "--file" ]]; then
  file="${2:-}"; shift 2 || shift $#
  if [[ -z "$file" || ! -f "$file" ]]; then
    echo "discord.sh: attachment not found: '$file' (sending text only)" >&2
    file=""
  fi
fi

msg="${1:-}"
[[ -z "$msg" && ! -t 0 ]] && msg="$(cat)"
[[ -z "$msg" && -z "$file" ]] && { echo "discord.sh: empty message" >&2; exit 0; }

if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
  echo "discord.sh: DISCORD_WEBHOOK_URL not set; message follows" >&2
  echo "$msg"
  [[ -n "$file" ]] && echo "[attachment: $file]"
  exit 0
fi

PY="$(command -v python3 || command -v python)"
# Discord caps content at 2000 chars; JSON-encode safely (quotes, newlines, emoji).
body="$("$PY" -c 'import json,sys; t=sys.argv[1]; print(json.dumps({"content": t if len(t) <= 1990 else t[:1987] + "...", "allowed_mentions": {"parse": []}}))' "$msg")"

if [[ -n "$file" ]]; then
  # multipart upload via python requests (portable; avoids curl -F quoting pitfalls)
  code="$("$PY" - "$DISCORD_WEBHOOK_URL" "$body" "$file" <<'EOF' 2>/dev/null
import os, sys, requests
url, body, path = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(path, "rb") as fh:
        r = requests.post(url, data={"payload_json": body},
                          files={"files[0]": (os.path.basename(path), fh)}, timeout=60)
    print(r.status_code)
except Exception:
    print("000")
EOF
)"
else
  code="$(curl -sS -o /dev/null -w '%{http_code}' -X POST "$DISCORD_WEBHOOK_URL" \
    -H "Content-Type: application/json" -d "$body" 2>/dev/null)"
fi
if [[ "$code" == "204" || "$code" == "200" ]]; then
  echo "discord.sh: sent${file:+ with $(basename "$file")}"
else
  echo "discord.sh: send FAILED (HTTP $code)" >&2
fi
exit 0
