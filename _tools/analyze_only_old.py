# -*- coding: utf-8 -*-
"""分析仅库内有的 87 篇：状态与正文量"""
import os, re, io

NEW = r"D:/workspace/ai_kb_base/_ynote_export"
OLD = r"D:/workspace/ai_kb_base/second-brain/raw/文档"

def rels(base):
    out = set()
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".md"):
                out.add(os.path.relpath(os.path.join(root, fn), base).replace("\\", "/"))
    return out

n, o = rels(NEW), rels(OLD)
only_old = sorted(o - n)
only_new = sorted(n - o)

def parse(p):
    s = io.open(p, encoding="utf-8").read()
    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
    body = s
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        body = s[m.end():]
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"[\s#*`>|]", "", body)
    return fm, len(body)

print("### 仅库内有 %d 篇 —— 状态分布 ###" % len(only_old))
stat = {}
rows = []
for rel in only_old:
    fm, ln = parse(os.path.join(OLD, rel))
    st = fm.get("content_status", "?")
    stat[st] = stat.get(st, 0) + 1
    rows.append((ln, st, fm.get("confidence", "?"), rel))
for k, v in sorted(stat.items(), key=lambda x: -x[1]):
    print("  %-14s %d 篇" % (k, v))

print("\n### 正文 >= 100 字的（内容有效，可保留旧版） ###")
valid = [r for r in rows if r[0] >= 100]
print("共 %d 篇" % len(valid))
for ln, st, cf, rel in sorted(valid, reverse=True)[:15]:
    print("  %5d字 %-12s %s" % (ln, st, rel))

print("\n### 正文 < 100 字的（空壳，缺内容） ###")
weak = [r for r in rows if r[0] < 100]
print("共 %d 篇" % len(weak))
for ln, st, cf, rel in sorted(weak, reverse=True)[:20]:
    print("  %5d字 %-12s %s" % (ln, st, rel))

print("\n### 仅新导出有 %d 篇 ###" % len(only_new))
for rel in only_new:
    fm, ln = parse(os.path.join(NEW, rel))
    print("  %5d字  %s" % (ln, rel))
