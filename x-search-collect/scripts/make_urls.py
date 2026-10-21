#!/usr/bin/env python3
"""Print X search URLs (Latest tab) for every query in x_queries.json.
usage: make_urls.py x_queries.json [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--lang en] [--ids q01,q02]"""
import argparse, json, urllib.parse
ap = argparse.ArgumentParser(); ap.add_argument("queries"); ap.add_argument("--since"); ap.add_argument("--until"); ap.add_argument("--lang"); ap.add_argument("--ids")
a = ap.parse_args(); cfg = json.load(open(a.queries, encoding="utf-8"))
suffix = cfg.get("suffix", "")
if a.lang or a.since or a.until:
    suffix = " " + " ".join(x for x in [f"lang:{a.lang}" if a.lang else "", f"since:{a.since}" if a.since else "", f"until:{a.until}" if a.until else ""] if x)
want = set(a.ids.split(",")) if a.ids else None
for q in cfg["queries"]:
    if want and q["id"] not in want: continue
    print(q["id"], "https://x.com/search?q=" + urllib.parse.quote(q["q"] + suffix) + "&src=typed_query&f=live")
