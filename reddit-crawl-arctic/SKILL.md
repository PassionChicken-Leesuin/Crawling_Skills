---
name: reddit-crawl-arctic
description: Collect Reddit posts and comments from chosen subreddits for a date range through the Arctic Shift API (no Reddit API key, no login), filter them locally with keyword groups, pull full comment trees for the posts that matter, and export analysis-ready CSVs. Use this whenever the user wants to crawl, scrape, collect, or build a corpus from Reddit — subreddits, community discourse, user experiences, "레딧 크롤링", "커뮤니티 수집", posts and comments for discourse/keyword/sentiment/laddering analysis — even if they don't say "Arctic Shift", and especially when direct Reddit access (JSON endpoints, Pushshift, PullPush) fails with 403/429.
---

# Reddit crawl via Arctic Shift

Arctic Shift mirrors Reddit and serves it through a free API with proper date filters. The bundled script turns it into a resumable pipeline: paginate every post of a subreddit for a date window → keep the ones that match keyword groups → fetch the full comment tree of the strongest matches → export CSVs. Everything is plain Python (stdlib only).

Read `references/arctic-shift-api.md` when you need endpoint or parameter details.

## What you need from the user (or decide yourself)

1. **Subreddits** — order them by relevance; big general subreddits (r/ChatGPT, r/programming) are mostly noise and dominate run time, so put them last or skip them. A "contrast group" of 3–5 general subreddits is enough to show the topic is concentrated somewhere.
2. **Date window** — three months of an active subreddit is ~20–30k posts and ~30 min.
3. **Keyword groups** — copy `assets/keywords.template.json`, one group per theme, lower-case substrings. Drop generic words early ("attention", "resume", "empty"): they produce most of the noise. Put affect/emotion words in a `secondary_groups` entry so they don't inflate the relevance score. `assets/keywords.ucd-example.json` is a worked example (AI-agent delegation study).
4. **Output folder** — the script keeps `raw/` (jsonl, never modified), CSVs, and per-mode state files there.

## Workflow

```bash
SK=~/.claude/skills/reddit-crawl-arctic/scripts/reddit_arctic.py
DATA=<project>/data/reddit

# 0. size it first (indexed counts + average posts/day; recent rate is usually 2–5x higher)
python3 "$SK" meta --data "$DATA" --subs ClaudeAI,ClaudeCode,cursor

# 1. posts — run in the background with a log; resumable, so stop/restart freely
python3 "$SK" posts --data "$DATA" --subs ClaudeAI,ClaudeCode,cursor --after 2026-07-20 --before 2026-10-20 > "$DATA/../posts.log" 2>&1 &

# 2. filter → posts_all.csv, posts_filtered.csv (sorted by core_groups, n_hits)
python3 "$SK" filter --data "$DATA" --keywords <project>/keywords.json

# 3. comment trees for strong matches (core_groups ≥ 2), gentle pacing
python3 "$SK" comments --data "$DATA" --keywords <project>/keywords.json --min-core 2 --sleep 2.5 > "$DATA/../comments.log" 2>&1 &

# re-export comment CSVs after changing keywords
python3 "$SK" export-comments --data "$DATA" --keywords <project>/keywords.json
```

Watch the logs for `DONE <n> items` per subreddit, and for `giving up` / `Traceback`. Use a Monitor or background task rather than polling.

## Things that will bite you (learned the hard way)

- **Keyword search on the server times out** for any active subreddit. Don't fight it: paginate by date (100/page) and filter locally. That is what the script does.
- **422 "Timeout. Maybe slow down a bit"** appears even on simple queries when the server is busy; the script backs off and retries up to 8 times. If a run dies anyway, just rerun the same command — state files make it resume at the last page.
- **One state file per mode.** `posts` writes `state_posts.json`, `comments` writes `state_comments.json`. Running both at the same time is fine; running two `posts` jobs on the same folder is not.
- **Partially crawled subreddit?** Move its `raw/posts_<sub>.jsonl` to `raw/_excluded/` before the final `filter`, otherwise its per-subreddit percentages are computed over a truncated window.
- **Scores are provisional** for posts younger than ~36 h (0/1 placeholders).
- **Comments are where the raw experiences live.** Posts are often announcements or "I built X"; the first-person detail is in comment trees, so always run step 3 for the matched posts.
- Browser-like User-Agent is already set; don't replace it with a "research bot" UA.

## Deliverables to hand back

| File | Content |
|---|---|
| `posts_all.csv` | every post in the window: id, date, subreddit, author, score, num_comments, flair, title, selftext, url |
| `posts_filtered.csv` | keyword matches + `core_groups`, `n_groups`, `n_hits`, `hit_groups`, `hit_terms` |
| `comments.csv` | full comment trees of the fetched posts (link_id, parent_id, depth, body, url) |
| `comments_filtered.csv` | comments that match keywords |
| `raw/*.jsonl` | untouched originals, resumable |

Write a short README next to the CSVs (row counts, columns, date window, which subreddits were skipped or partial). Downstream analysis (keyword trends, co-occurrence networks, laddering) reads these CSVs; keep ids so comments can be joined to posts.

## Ethics and scope

Only public posts are collected, through a public mirror, at a polite rate (~1 request/s). Don't store or publish usernames in reports; cite as "(Reddit r/<sub>, YYYY-MM)". If the user needs private subreddits, deleted content, or vote-level data, this route can't provide it — say so.
