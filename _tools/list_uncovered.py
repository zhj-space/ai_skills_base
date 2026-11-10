# -*- coding: utf-8 -*-
"""列出指定分类下未编译的 source，带字数"""
import os, re, io, sys

KB = r"D:/workspace/ai_kb_base/second-brain"
cov = set()
for fn in os.listdir(os.path.join(KB, "wiki", "summaries")):
    if fn.endswith(".md"):
        s = io.open(os.path.join(KB, "wiki", "summaries", fn), encoding="utf-8").read()
        m = re.search(r"^source_path:\s*(.+)$", s, re.M)
        if m:
            cov.add(m.group(1).strip().strip('"'))

cat = sys.argv[1] if len(sys.argv) > 1 else "大数据"
SRC = os.path.join(KB, "raw", "summaries", "个人资产体系", cat)

rows = []
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
        md = re.search(r"^modality:\s*(\S+)", s, re.M)
        rows.append((int(wc.group(1)) if wc else 0, md.group(1) if md else "?", rel))

print("[%s] 未编译 %d 篇" % (cat, len(rows)))
for w, m, rel in sorted(rows, reverse=True):
    print("  %5d 字 %-12s %s" % (w, m, rel.replace("raw/docs/personal-assets/", "")))
