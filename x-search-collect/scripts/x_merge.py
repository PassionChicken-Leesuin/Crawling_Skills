#!/usr/bin/env python3
"""Merge collector dumps (raw/q*.json) into x_posts.csv: dedupe across queries, tag queries/groups, optional keyword hits and date window.
usage: x_merge.py <data/x dir> --queries x_queries.json [--keywords keywords.json] [--window 2026-07-20 2026-10-20]"""
import argparse, csv, glob, json, os
ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("--queries", required=True); ap.add_argument("--keywords"); ap.add_argument("--window", nargs=2, metavar=("START", "END"))
a = ap.parse_args()
qmeta = {q["id"]: q for q in json.load(open(a.queries, encoding="utf-8"))["queries"]}
groups, ctx = {}, []
if a.keywords:
    kw = json.load(open(a.keywords, encoding="utf-8"))
    groups = {g: [t.lower() for t in ts] for g, ts in kw["groups"].items()}
    ctx = [c.lower() for c in kw.get("context_terms", kw.get("agentic_context", []))]
posts = {}
for fn in sorted(glob.glob(os.path.join(a.data, "raw", "q*.json"))):
    d = json.load(open(fn, encoding="utf-8")); qid = d["query_id"]
    for it in d["items"]:
        p = posts.setdefault(it["id"], dict(it, queries=set())); p["queries"].add(qid)
        if len(it.get("text", "")) > len(p.get("text", "")): p["text"] = it["text"]
rows = []
for pid, p in posts.items():
    t = (p.get("text") or "").lower()
    hits = {g: [x for x in ts if x in t] for g, ts in groups.items()}; hits = {g: v for g, v in hits.items() if v}
    qids = sorted(p["queries"]); base = qids[0].split("_")[0]
    date = (p.get("time") or "")[:10]
    rows.append({"id": pid, "date": date, "in_window": int(a.window[0] <= date <= a.window[1]) if a.window else "", "user": p.get("user", ""),
                 "is_reply": int(bool(p.get("replying"))), "likes": p.get("like", ""), "replies": p.get("reply", ""), "reposts": p.get("rt", ""),
                 "queries": ";".join(qids), "query_groups": ";".join(sorted({qmeta[q.split("_")[0]]["group"] for q in qids if q.split("_")[0] in qmeta})),
                 "context": int(any(c in t for c in ctx)) if ctx else "", "n_groups": len(hits), "n_hits": sum(len(v) for v in hits.values()),
                 "hit_groups": ";".join(hits), "hit_terms": ";".join(sorted({x for v in hits.values() for x in v})),
                 "text": p.get("text", ""), "url": f"https://x.com/{p.get('user', 'i')}/status/{pid}", "time": p.get("time", "")})
rows.sort(key=lambda r: (-r["n_groups"], -r["n_hits"], r["date"]))
cols = list(rows[0].keys()) if rows else []
with open(os.path.join(a.data, "x_posts.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
if a.window:
    win = [r for r in rows if r["in_window"] == 1]
    with open(os.path.join(a.data, "x_posts_window.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(win)
    print(f"in window {a.window[0]}..{a.window[1]}: {len(win)} -> x_posts_window.csv")
by_month = {}
for r in rows: by_month[r["date"][:7]] = by_month.get(r["date"][:7], 0) + 1
print(f"x_merge: {len(rows)} unique posts from {len(glob.glob(os.path.join(a.data, 'raw', 'q*.json')))} dumps -> x_posts.csv; by month: {dict(sorted(by_month.items()))}")
