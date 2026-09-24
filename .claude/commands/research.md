---
description: Claude web research — default month-end scan of the 12 ETFs + macro, or a custom topic
argument-hint: "[topic or question]"
---
Research with your own **WebSearch** tool, plus **WebFetch** to read a specific page when a result needs checking. **Context only**: nothing here changes RAAM signals or weights. No API key or script is involved.

If `$ARGUMENTS` is empty, run the **default month-end scan**:
1. **Structural check per ETF.** For each of VV, IJH, IJR, EFA, EEM, RWR, DBC, VAW, AGG, TIP, IGOV, BIL and SPY (Core), look for anything announced in the past ~45 days: fund closures or liquidations, mergers, ticker changes, index or methodology changes, trading halts, or unusual distributions or splits. Prefer the issuer's site (iShares, Vanguard, SSGA/State Street, Invesco) and reputable news. You may group tickers per issuer to keep the searches few, about 4–6 searches in total.
2. **Macro backdrop.** Search for this month's key drivers across US and international equities, REITs, commodities, US Treasuries/TIPS and international government bonds. Summarise them in about 6 dated bullets.

Otherwise, research the topic in `$ARGUMENTS`, focusing on the last week unless the topic implies otherwise. Keep it to a few searches.

Rules:
- Cite only pages you actually saw in search results or fetched. Never invent a source, date or event. If you find nothing, say "none found".
- A **flag** means a *structural* issue with a universe ETF: closure, merger, delisting, ticker or index change, or trading halt. Price moves and news commentary are not flags.
- If web search is unavailable or a fetch is blocked (e.g. `host_not_allowed`), log "research limited: <reason>" and continue. Research failure never blocks the run.

Then:
- Prepend an entry to `memory/RESEARCH-LOG.md`, below the header:
  - `## <YYYY-MM-DD> — <topic>`
  - what you searched for;
  - a 3–6 bullet summary;
  - **Flags:** the flags, or "none";
  - sources as a list of URLs.
- When research runs from within another command, hand the flags back to that command; it sends the Discord message. When run on its own, reply with the summary; no Discord message is needed.
