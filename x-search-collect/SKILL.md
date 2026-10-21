---
name: x-search-collect
description: Collect X (Twitter) posts for a set of search queries through the built-in browser using the user's own logged-in X session — no API key, no paid tier, no third-party scraper. Injects an auto-scroll collector into x.com search results, gets the data onto disk despite X's Content-Security-Policy (oversized-tool-result file trick), extracts and merges everything into x_posts.csv with query tags and keyword hits. Use this whenever the user wants to crawl, scrape, collect, or build a corpus of tweets / X posts / Twitter search results ("트위터 크롤링", "X 수집", public opinion or user experiences on X), says they can log in to X in the browser, or when X API access is unavailable or too expensive.
---

# X search collection through the logged-in browser

X's web search works only when logged in, the free API tier cannot read, and the page's CSP blocks any attempt to POST scraped data out of the page. This skill works around all three with the built-in browser (`mcp__Claude_Browser__*` tools): the **user logs in themselves**, you drive search pages, a small injected script harvests the rendered posts, and you move the data to disk by making the tool result so large that the harness writes it to a file. Reading ~1,900 posts this way cost almost no context.

Never type credentials or touch the login form; open `https://x.com/login` and ask the user to sign in, then verify by reading the page (a `Profile` link / avatar in the left nav means logged in).

## Inputs

- **Queries**: copy `assets/x_queries.template.json` → one entry per theme (`id`, `group`, `q`). X search syntax: `"exact phrase"`, `OR`, parentheses, `lang:en`, `since:YYYY-MM-DD until:YYYY-MM-DD`. Keep phrase queries specific; broad single words return noise. 20–35 queries is a comfortable session. `assets/x_queries.ucd-example.json` is a worked set (AI-agent delegation experiences).
- **Cap per query** (default 120). The Latest tab yields ~20 posts per scroll page; 120 ≈ 6 pages.
- **Output folder** `<project>/data/x/` with `raw/` for per-query dumps.

## Workflow (per query, ~1–2 min; run 2–3 tabs in parallel)

1. Build URLs: `python3 scripts/make_urls.py x_queries.json` (Latest tab, `f=live`).
2. `navigate` the tab to the URL, `wait` 7–10 s (the SPA renders slowly; read `article` count via JS to confirm). The first load after a cold start may show spinners only — a `tabs_select`/re-navigate fixes it.
3. Inject `scripts/collector.js` with `javascript_tool` after replacing `__QID__` and `__CAP__`. It scrolls every 1.5 s, harvests `article[data-testid="tweet"]` before each scroll (X virtualises the list), dedupes by status id, and stops on 8 idle rounds, the cap, 80 rounds, or an error banner.
4. Poll with `scripts/status.js` every ~30 s (`done`, `n`, `err`).
5. When done, run `scripts/dump.js` **before navigating away**. The returned string is deliberately ~200 KB, so the harness saves it to `…/tool-results/<call>.txt` and shows only the path. Then:
   `python3 scripts/x_extract.py <that .txt file> <project>/data/x/raw` → writes `raw/<qid>.json`.
   Batch several tabs' dumps in one `browser_batch` call: the whole batch is saved to one file and `x_extract.py` pulls every `{"qid":…}` object out of it. You can put the next `navigate` + collector injection for each tab in the same batch, after its dump.
6. After all queries: `python3 scripts/x_merge.py <project>/data/x --queries x_queries.json [--keywords keywords.json] [--window START END]` → `x_posts.csv` (+ `x_posts_window.csv`).

A useful batch shape: `[dump tab A, dump tab B, navigate A → next URL, navigate B → next URL, wait 10, inject A, inject B, status tab C]`.

## Limits you will hit

- **Rate limit**: roughly 40–50 search-timeline requests per 15 minutes per account. The page then shows "Something went wrong. Try reloading", the collector sets `err: "error-banner"`, and new searches return nothing. Dump whatever was collected, stop, and wait ~15 minutes (a background `until` timer, not foreground sleep). Pace at ~6–8 capped queries per 15-minute window.
- **History is shallow**: `since:`/`until:` do not unlock older posts — monthly windows for a 3-month range returned 7–9 posts each while the open query returned 120 recent ones. Expect a recency bias (most posts from the last 2–4 weeks); say so in the report and keep X for qualitative quotes rather than time-series.
- **Dates outside the window** appear anyway (replies and quotes); `x_merge.py --window` flags `in_window`.
- Replies are included (`is_reply`); harvest text is the visible tweet text only (no thread expansion). If reply threads matter, open individual status pages for a curated few — it is slow and counts against the same rate limit.
- Background tabs work; `navigate` resets `window.__xcol`, so always dump first.
- `fetch()` to localhost from x.com fails with "Failed to fetch" (CSP `connect-src`). Don't build a receiver server; use the file trick.

## Deliverables

`x_posts.csv`: id, date, in_window, user, is_reply, likes, replies, reposts, queries, query_groups, context, n_groups, n_hits, hit_groups, hit_terms, text, url, time. Report counts per query, unique posts, month distribution, and how many rate-limit pauses happened. In write-ups cite posts as "(X, YYYY-MM)" without handles.

## Ethics

Public posts visible to the logged-in user only, at human-like pace, for research the user asked for. Don't collect DMs, protected accounts, or anything behind the user's follows; don't act on the account (no likes, follows, posts).
