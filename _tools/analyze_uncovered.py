# -*- coding: utf-8 -*-
"""未编译 source 的字数与模态分布"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")

cov = set()
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = re.search(r"^source_path:\s*(.+)$", s, re.M)
    if m:
        cov.add(m.group(1).strip().strip('"'))

print("已编译 source_path 记录：%d 条" % len(cov))

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
        rows.append((rel, int(wc.group(1)) if wc else 0, md.group(1) if md else "?"))

print("未编译 %d 篇" % len(rows))

b = collections.Counter()
for _, w, m in rows:
    if w < 60:
        b["① <60 字（纯图/空）"] += 1
    elif w < 200:
        b["② 60-200 字（短笔记）"] += 1
    elif w < 600:
        b["③ 200-600 字（中等）"] += 1
    else:
        b["④ >600 字（长文）"] += 1
for k in sorted(b):
    print("  %-24s %d 篇" % (k, b[k]))

print("\n=== 按 modality ===")
for k, v in collections.Counter(m for _, _, m in rows).most_common():
    print("  %-14s %d" % (k, v))

print("\n=== 长文 top 15（优先编译对象）===")
for rel, w, m in sorted(rows, key=lambda x: -x[1])[:15]:
    print("  %5d 字 %-14s %s" % (w, m, rel.replace("raw/docs/personal-assets/", "")))

print("\n=== 纯图篇（不建页，只在 sources 留存）前 10 ===")
imgs = [r for r in rows if r[1] < 60]
print("共 %d 篇" % len(imgs))
for rel, w, m in imgs[:10]:
    print("  %5d 字 %s" % (w, rel.replace("raw/docs/personal-assets/", "")))
