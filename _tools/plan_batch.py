# -*- coding: utf-8 -*-
"""按分类统计未编译 source 的可编译性（≥60 字才算可编译）"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
cov = set()
for fn in os.listdir(os.path.join(KB, "wiki", "summaries")):
    if fn.endswith(".md"):
        s = io.open(os.path.join(KB, "wiki", "summaries", fn), encoding="utf-8").read()
        m = re.search(r"^source_path:\s*(.+)$", s, re.M)
        if m:
            cov.add(m.group(1).strip().strip('"'))

SRC = os.path.join(KB, "raw", "summaries", "个人资产体系")
stat = collections.defaultdict(lambda: [0, 0, 0])  # [可编译, 纯图/空, 字数合计]

for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, KB).replace(os.sep, "/")
        if rel in cov:
            continue
        s = io.open(p, encoding="utf-8").read()
        wc = re.search(r"^word_count:\s*(\d+)", s, re.M)
        w = int(wc.group(1)) if wc else 0
        cat = rel.replace("raw/docs/personal-assets/", "").split("/")[0]
        if w >= 60:
            stat[cat][0] += 1
            stat[cat][2] += w
        else:
            stat[cat][1] += 1

print("%-14s %8s %8s %10s" % ("分类", "可编译", "纯图/空", "总字数"))
print("-" * 46)
tc = ti = tw = 0
for k, (c, i, w) in sorted(stat.items(), key=lambda x: -x[1][0]):
    print("%-14s %8d %8d %10d" % (k, c, i, w))
    tc += c
    ti += i
    tw += w
print("-" * 46)
print("%-14s %8d %8d %10d" % ("合计", tc, ti, tw))
