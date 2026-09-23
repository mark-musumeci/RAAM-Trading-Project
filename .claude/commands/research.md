---
description: Perplexity research — default month-end scan of the 12 ETFs + macro, or a custom topic
argument-hint: "[topic or question]"
---
Research via Perplexity. **Context only**: nothing here changes RAAM signals or weights.

If `$ARGUMENTS` is empty, run the **default scan**, which is exactly two queries:
1. `bash scripts/perplexity.sh "Any fund closures, mergers, liquidations, ticker changes, index changes, trading halts or unusual distributions announced in the past 45 days for these ETFs: VV, IJH, IJR, EFA, EEM, RWR, DBC, VAW, AGG, TIP, IGOV, SHY? Answer per ticker; say none found if nothing." month`
2. `bash scripts/perplexity.sh "Summarize this month's key drivers across US and international equities, REITs, commodities, US Treasuries/TIPS and international government bonds, in 6 bullet points with dates." month`

Otherwise, run a single query built from `$ARGUMENTS`, with recency `week` unless the topic implies otherwise.

Then:
- Prepend an entry to `memory/RESEARCH-LOG.md`, below the header:
  - `## <YYYY-MM-DD> — <topic>`
  - the question(s);
  - a 3–6 bullet summary;
  - **Flags:** any structural issue with a universe ETF, or "none";
  - sources as a list of URLs.
- If `perplexity.sh` says the key is not set or the request failed, log "research skipped: <reason>" and continue. Research failure never blocks the run.
- When research runs from within another command, hand the flags back to that command; it sends the WhatsApp message. When run on its own, reply with the summary; no WhatsApp is needed.
