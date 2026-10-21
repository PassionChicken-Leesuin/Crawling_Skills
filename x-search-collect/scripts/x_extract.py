#!/usr/bin/env python3
"""Extract X collector dumps from a saved browser tool-result file.
Each javascript result is expected to be a JSON string of {"qid":..., "n":..., "items":[[id,user,time,text,reply,rt,like,replying],...]} (optionally followed by filler).
Writes <out>/<qid>.json and prints a summary. Usage: x_extract.py <toolresult.txt> <out_dir>
"""
import json, re, sys, os, datetime
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
raw = open(src, encoding="utf-8").read()
try:
    parts = json.loads(raw)
    texts = [p.get("text", "") for p in parts] if isinstance(parts, list) else [raw]
except Exception:
    texts = [raw]
found = 0
for t in texts:
    # the JS result is rendered as a JSON string literal; find every "{\"qid\":...}" literal
    for m in re.finditer(r'"(\{\\"qid\\".*?)"(?=\s*\n|\s*$|\s*\(captured)', t, flags=re.S):
        lit = '"' + m.group(1) + '"'
        try:
            s = json.loads(lit)           # unescape string literal
            s = s.split("\n__FILLER__")[0]
            obj = json.loads(s)
        except Exception as e:
            continue
        qid = obj.get("qid"); items = obj.get("items", [])
        rows = [{"id": i[0], "user": i[1], "time": i[2], "text": i[3], "reply": i[4], "rt": i[5], "like": i[6], "replying": bool(i[7])} for i in items]
        path = os.path.join(out, f"{qid}.json")
        json.dump({"query_id": qid, "saved_at": datetime.datetime.now().isoformat(), "n": len(rows), "items": rows}, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(f"saved {qid}: {len(rows)} items -> {path}")
        found += 1
    # status objects (not JSON strings) just print
    for m in re.finditer(r'\{\s*"done":.*?\}', t, flags=re.S):
        print("status:", re.sub(r"\s+", " ", m.group(0))[:200])
if not found:
    print("no dumps found")
