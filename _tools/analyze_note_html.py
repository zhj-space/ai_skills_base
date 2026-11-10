# -*- coding: utf-8 -*-
"""分析 90 个 .note(HTML) 文件的结构"""
import os, re, io, collections

BASE = r"D:/workspace/ai_kb_base/_ynote_export"

files = []
for root, _, fs in os.walk(BASE):
    for fn in fs:
        if fn.endswith(".note"):
            files.append(os.path.join(root, fn))

print("共 %d 个 .note" % len(files))

tags = collections.Counter()
imgs = []
srcs = collections.Counter()
total_chars = 0

for p in files:
    s = io.open(p, encoding="utf-8", errors="replace").read()
    total_chars += len(s)
    for t in re.findall(r"<([a-zA-Z][a-zA-Z0-9]*)", s):
        tags[t.lower()] += 1
    for m in re.finditer(r'<img[^>]*src="([^"]+)"', s):
        imgs.append(m.group(1))
        srcs[m.group(1).split("/")[2] if "//" in m.group(1) else "relative"] += 1

print("总字符：%d" % total_chars)
print("\n=== 标签分布 ===")
for t, c in tags.most_common(25):
    print("  %-12s %d" % (t, c))
print("\n=== 图片总数：%d ===" % len(imgs))
print("=== 图片域名分布 ===")
for d, c in srcs.most_common():
    print("  %-30s %d" % (d, c))
print("\n=== 图片 URL 样例 ===")
for u in imgs[:6]:
    print("  " + u)
