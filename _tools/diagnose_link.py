# -*- coding: utf-8 -*-
"""诊断：为什么 [[digest-index]] 没被判为断链"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
all_md = []
for root, _, files in os.walk(KB):
    for fn in files:
        if fn.endswith(".md"):
            all_md.append(os.path.join(root, fn))

pages = {}
for p in all_md:
    pages.setdefault(os.path.splitext(os.path.basename(p))[0], []).append(p)

print("pages 中 '沉淀索引' 出现次数：%d" % len(pages.get("沉淀索引", [])))
for p in pages.get("沉淀索引", []):
    print("   ", p)

idx = os.path.join(KB, "index.md")
s = io.open(idx, encoding="utf-8").read()
links = re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", s)
print("\nindex.md 链接总数：%d" % len(links))
print("其中含『沉淀』的：%s" % [x for x in links if "analysis" in x])
print("其中含『主题』的：%s" % [x for x in links if "主题" in x])
miss = sorted({x.strip() for x in links if x.strip() not in pages})
print("\n真正缺失：%d -> %s" % (len(miss), miss[:10]))
