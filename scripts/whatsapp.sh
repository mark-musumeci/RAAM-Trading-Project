#!/usr/bin/env bash
# Send a WhatsApp message. Never fails the caller: notification problems must not block trading.
#
# Usage: whatsapp.sh "message text"      (or pipe text on stdin)
# Backend via WHATSAPP_BACKEND: callmebot (default) | twilio | console
#   callmebot: CALLMEBOT_PHONE, CALLMEBOT_APIKEY   (one-time opt-in: https://www.callmebot.com/blog/free-api-whatsapp-messages/)
#   twilio:    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then set -a; source "$ROOT/.env"; set +a; fi

msg="${1:-}"
[[ -z "$msg" && ! -t 0 ]] && msg="$(cat)"
[[ -z "$msg" ]] && { echo "whatsapp.sh: empty message" >&2; exit 0; }
msg="${msg:0:1500}"   # keep well under provider limits

backend="${WHATSAPP_BACKEND:-callmebot}"
case "$backend" in
  callmebot)
    if [[ -z "${CALLMEBOT_PHONE:-}" || -z "${CALLMEBOT_APIKEY:-}" ]]; then
      echo "whatsapp.sh: CallMeBot not configured; message follows" >&2; echo "$msg"; exit 0
    fi
    out="$(curl -sS -G "https://api.callmebot.com/whatsapp.php" \
      --data-urlencode "phone=$CALLMEBOT_PHONE" \
      --data-urlencode "text=$msg" \
      --data-urlencode "apikey=$CALLMEBOT_APIKEY" 2>&1)" \
      && echo "whatsapp.sh: sent via CallMeBot" \
      || echo "whatsapp.sh: CallMeBot send FAILED: ${out:0:300}" >&2
    ;;
  twilio)
    if [[ -z "${TWILIO_ACCOUNT_SID:-}" || -z "${TWILIO_AUTH_TOKEN:-}" ]]; then
      echo "whatsapp.sh: Twilio not configured; message follows" >&2; echo "$msg"; exit 0
    fi
    out="$(curl -sS -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
      -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
      --data-urlencode "From=${TWILIO_WHATSAPP_FROM:-whatsapp:+14155238886}" \
      --data-urlencode "To=${TWILIO_WHATSAPP_TO:?}" \
      --data-urlencode "Body=$msg" 2>&1)" \
      && echo "whatsapp.sh: sent via Twilio" \
      || echo "whatsapp.sh: Twilio send FAILED: ${out:0:300}" >&2
    ;;
  *)
    echo "$msg"
    ;;
esac
exit 0
