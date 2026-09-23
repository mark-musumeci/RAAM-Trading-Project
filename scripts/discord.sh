#!/usr/bin/env bash
# Post a message to the RAAM Discord channel via webhook.
# Never fails the caller: notification problems must not block trading.
#
# Usage: discord.sh "message text"      (or pipe text on stdin)
# Needs env var DISCORD_WEBHOOK_URL (cloud environment variable; local .env for testing).
# If it is unset, the message is printed to stdout instead.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_env.sh"
load_env "$ROOT"

msg="${1:-}"
[[ -z "$msg" && ! -t 0 ]] && msg="$(cat)"
[[ -z "$msg" ]] && { echo "discord.sh: empty message" >&2; exit 0; }

if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
  echo "discord.sh: DISCORD_WEBHOOK_URL not set; message follows" >&2
  echo "$msg"
  exit 0
fi

PY="$(command -v python3 || command -v python)"
# Discord caps content at 2000 chars; JSON-encode safely (quotes, newlines, emoji).
body="$("$PY" -c 'import json,sys; t=sys.argv[1]; print(json.dumps({"content": t if len(t) <= 1990 else t[:1987] + "...", "allowed_mentions": {"parse": []}}))' "$msg")"

code="$(curl -sS -o /dev/null -w '%{http_code}' -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" -d "$body" 2>/dev/null)"
if [[ "$code" == "204" || "$code" == "200" ]]; then
  echo "discord.sh: sent"
else
  echo "discord.sh: send FAILED (HTTP $code)" >&2
fi
exit 0
