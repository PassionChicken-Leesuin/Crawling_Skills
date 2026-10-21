# Arctic Shift API — condensed notes (verified 2026-10-20)

Base URL: `https://arctic-shift.photon-reddit.com` · Docs: github.com/ArthurHeitmann/arctic_shift/blob/master/api/README.md · Free, no auth, no uptime guarantee. Send a browser-like User-Agent; requests with a custom/research UA were answered with 422 "Timeout" far more often.

## Endpoints
| Endpoint | Use |
|---|---|
| `/api/posts/search` | posts by `subreddit`, `after`, `before`, `limit` (1–100 or `auto`), `sort` (asc/desc), `fields` |
| `/api/comments/search` | same for comments (`body`, `link_id`, `parent_id` params) |
| `/api/comments/tree?link_id=t3_<id>&limit=9999` | whole comment tree of one post (fast, id-based) |
| `/api/posts/ids?ids=a,b,c` · `/api/comments/ids` | lookup by id (≤500) |
| `/api/subreddits/search?subreddit=<name>` | `_meta.num_posts`, `_meta.num_comments`, `earliest_post` → volume estimate |
| `/api/posts/search/aggregate?aggregate=created_utc&frequency=month&...` | time series; **times out on large subreddits** |

## Parameters
- `after` / `before`: epoch seconds, epoch ms, ISO (`2026-07-20`), or relative (`3m`, `2d`). Pagination: `sort=asc`, set `after` = last `created_utc` − 1 and dedupe by `id`.
- `fields` (posts): `id, created_utc, subreddit, author, title, selftext, score, num_comments, url, link_flair_text, over_18, crosspost_parent, post_hint, spoiler`. Comments: `id, created_utc, subreddit, author, body, score, link_id, parent_id`. `permalink` is **not** a valid field (400) — build it: `https://www.reddit.com/r/<sub>/comments/<id>/`.
- Keyword search params `query`, `title`, `selftext`, `body`, `author_flair_text`: only together with `subreddit`/`author`, and **not supported on very active subreddits** (returns 422 "Timeout. Maybe slow down a bit"). Treat keyword search as unavailable; paginate by date and filter locally.

## Behaviour
- ~100 items per request, 1–4 s each. Under load the server returns 422 `{"error":"Timeout. Maybe slow down a bit"}` even for simple queries — back off (5 → 10 → 20 … s) and retry; it recovers.
- 429 = rate limited; honour `X-RateLimit-Reset` (seconds).
- Items younger than ~36 h have `score`/`num_comments` = 0/1 (archived at post time, updated later).
- IDs are base36, optionally prefixed `t3_` (posts) / `t1_` (comments).
- Throughput seen: r/ClaudeAI 26,949 posts (3 months) in ~36 min; 17 subreddits ≈ 130k posts in ~2.5 h with retries.

## Alternatives that did NOT work (2026-10)
- Reddit public JSON (`/r/x/search.json`) → 403 without OAuth.
- PullPush (`api.pullpush.io`) → 429 "does not provide free scraping resources for agents".
- Reddit official API (PRAW) works with an app registration but has weak date filters and capped search results; use it only as a supplement.
