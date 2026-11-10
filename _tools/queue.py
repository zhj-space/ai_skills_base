# -*- coding: utf-8 -*-
"""列出所有未编译的可编译 source，按分类分组，带字数"""
import os, re, io, collections, sys

KB = r"D:/workspace/ai_kb_base/second-brain"
cov = set()
for fn in os.listdir(os.path.join(KB, "wiki", "summaries")):
    if fn.endswith(".md"):
        s = io.open(os.path.join(KB, "wiki", "summaries", fn), encoding="utf-8").read()
        m = re.search(r"^source_path:\s*(.+)$", s, re.M)
        if m:
            cov.add(m.group(1).strip().strip('"'))

SRC = os.path.join(KB, "raw", "summaries", "个人资产体系")
by = collections.defaultdict(list)
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
        if w < 60:
            continue
        cat = rel.replace("raw/docs/personal-assets/", "").split("/")[0]
        by[cat].append((w, rel))

order = sorted(by, key=lambda c: (len(by[c]), c))
print("可编译分类（按篇数升序）：")
for c in order:
    print("  %-14s %3d 篇   %6d 字" % (c, len(by[c]), sum(x[0] for x in by[c])))

target = sys.argv[1] if len(sys.argv) > 1 else None
if target:
    print("\n=== %s ===" % target)
    for w, rel in sorted(by.get(target, [])):
        print("  %5d 字  %s" % (w, rel.replace("raw/docs/personal-assets/", "")))
