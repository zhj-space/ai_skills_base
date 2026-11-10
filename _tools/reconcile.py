# -*- coding: utf-8 -*-
"""新旧两边路径对账"""
import os, io, json

NEW = r"D:/workspace/ai_kb_base/_ynote_export"
OLD = r"D:/workspace/ai_kb_base/second-brain/raw/文档"

def rels(base):
    out = set()
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".md"):
                out.add(os.path.relpath(os.path.join(root, fn), base).replace("\\", "/"))
    return out

n = rels(NEW)
o = rels(OLD)
print("新导出：%d 篇" % len(n))
print("库内旧版：%d 篇" % len(o))
print("两边都有：%d 篇" % len(n & o))
print("仅新导出有：%d 篇" % len(n - o))
print("仅库内有：%d 篇" % len(o - n))
print("\n=== 仅库内有（新导出缺失） ===")
for x in sorted(o - n):
    print("  " + x)
print("\n=== 仅新导出有 ===")
for x in sorted(n - o):
    print("  " + x)
