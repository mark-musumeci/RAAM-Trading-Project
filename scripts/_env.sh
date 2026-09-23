#!/usr/bin/env bash
# Sourced by the other scripts. API keys come from ENVIRONMENT VARIABLES.
# - Cloud routines (CLAUDE_CODE_REMOTE=true): only the cloud environment's variables are used;
#   a .env file is never read, even if one exists.
# - Local use: .env may fill in variables that are NOT already set. Real env vars always win.
load_env() {
  local root="$1" f line key val
  [[ "${CLAUDE_CODE_REMOTE:-}" == "true" ]] && return 0
  f="$root/.env"
  [[ -f "$f" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" || "$line" == \#* || "$line" != *=* ]] && continue
    key="${line%%=*}"; key="${key//[[:space:]]/}"
    val="${line#*=}"
    [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
    [[ -n "${!key+x}" ]] && continue
    if [[ "$val" == \"*\" || "$val" == \'*\' ]]; then val="${val:1:${#val}-2}"; fi
    export "$key=$val"
  done < "$f"
}

# require_env VAR... -> exits 2 with a clear message naming the missing variable(s)
require_env() {
  local missing=() v
  for v in "$@"; do [[ -n "${!v:-}" ]] || missing+=("$v"); done
  if (( ${#missing[@]} )); then
    echo "{\"error\":\"missing environment variable(s): ${missing[*]} - set them in the cloud environment's Environment variables (or local .env for local testing)\"}" >&2
    exit 2
  fi
}
