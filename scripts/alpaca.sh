#!/usr/bin/env bash
# Thin Alpaca REST wrapper for ad-hoc checks and manual trades. Prints raw JSON.
# The routines use scripts/raam.py for signals and rebalancing; this is for /portfolio and /trade.
#
# Usage:
#   alpaca.sh account | positions | clock | orders [open|closed|all]
#   alpaca.sh position SYM | quote SYM | close SYM
#   alpaca.sh calendar START END            (YYYY-MM-DD)
#   alpaca.sh bars SYM [DAYS]               (daily bars, default 10 days, IEX feed)
#   alpaca.sh order SYM QTY buy|sell        (market, day; universe symbols only)
#   alpaca.sh cancel ORDER_ID|all
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then set -a; source "$ROOT/.env"; set +a; fi

BASE="${ALPACA_BASE_URL:-https://paper-api.alpaca.markets}"
DATA="${ALPACA_DATA_URL:-https://data.alpaca.markets}"
: "${ALPACA_API_KEY:?ALPACA_API_KEY not set}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set}"

if [[ "$BASE" != *paper-api* ]]; then
  if [[ "${PAPER_TRADING:-true}" != "false" || "${LIVE_CONFIRM:-no}" != "yes" ]]; then
    echo '{"error":"refusing non-paper endpoint; needs PAPER_TRADING=false and LIVE_CONFIRM=yes"}' >&2
    exit 2
  fi
fi

api() {  # api METHOD URL [JSON_BODY]
  local method="$1" url="$2" body="${3:-}"
  local args=(-sS -X "$method" "$url" -H "APCA-API-KEY-ID: $ALPACA_API_KEY"
              -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY")
  [[ -n "$body" ]] && args+=(-H "Content-Type: application/json" -d "$body")
  curl "${args[@]}"
  echo
}

universe() {
  local py; py="$(command -v python3 || command -v python)"
  "$py" -c "import json,sys; c=json.load(open(sys.argv[1])); print(' '.join(c['universe']['risk_assets']+[c['universe']['cash']]))" "$ROOT/config/raam.json"
}

cmd="${1:-}"; shift || true
case "$cmd" in
  account)   api GET "$BASE/v2/account" ;;
  positions) api GET "$BASE/v2/positions" ;;
  position)  api GET "$BASE/v2/positions/${1:?symbol}" ;;
  clock)     api GET "$BASE/v2/clock" ;;
  orders)    api GET "$BASE/v2/orders?status=${1:-open}&limit=50" ;;
  calendar)  api GET "$BASE/v2/calendar?start=${1:?start}&end=${2:?end}" ;;
  quote)     api GET "$DATA/v2/stocks/${1:?symbol}/trades/latest?feed=iex" ;;
  bars)
    sym="${1:?symbol}"; days="${2:-10}"
    start="$(date -u -d "-$((days * 2 + 5)) days" +%Y-%m-%d 2>/dev/null || date -u -v-$((days * 2 + 5))d +%Y-%m-%d)"
    api GET "$DATA/v2/stocks/bars?symbols=$sym&timeframe=1Day&start=$start&limit=$days&feed=iex&adjustment=all&sort=desc" ;;
  order)
    sym="${1:?symbol}"; qty="${2:?qty}"; side="${3:?buy|sell}"
    [[ "$side" == "buy" || "$side" == "sell" ]] || { echo '{"error":"side must be buy or sell"}' >&2; exit 2; }
    if ! grep -qw "$sym" <<<"$(universe)"; then
      echo "{\"error\":\"$sym is not in the RAAM universe: $(universe)\"}" >&2; exit 2
    fi
    api POST "$BASE/v2/orders" "{\"symbol\":\"$sym\",\"qty\":\"$qty\",\"side\":\"$side\",\"type\":\"market\",\"time_in_force\":\"day\"}" ;;
  close)     api DELETE "$BASE/v2/positions/${1:?symbol}" ;;
  cancel)
    if [[ "${1:?order id or all}" == "all" ]]; then api DELETE "$BASE/v2/orders"
    else api DELETE "$BASE/v2/orders/$1"; fi ;;
  *) sed -n '2,12p' "$0"; exit 1 ;;
esac
