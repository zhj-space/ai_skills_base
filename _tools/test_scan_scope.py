# -*- coding: utf-8 -*-
"""验证 verify_kb 的扫描范围是否包含 index.md 等根级文件"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"

def rels(base):
    out = []
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".md"):
                out.append(os.path.join(root, fn))
    return out

all_md = rels(KB)
print("全库 md 数：%d" % len(all_md))
root_files = [p for p in all_md if os.path.dirname(p) == KB]
print("根目录 md：%s" % [os.path.basename(p) for p in root_files])

pages = set()
for p in all_md:
    pages.add(os.path.splitext(os.path.basename(p))[0])

# 模拟 verify_kb 的循环
scanned = 0
idx_links = []
for p in all_md:
    if "_templates" in p or "/raw/" in p.replace("\\", "/"):
        continue
    scanned += 1
    if os.path.basename(p) == "index.md":
        s = io.open(p, encoding="utf-8").read()
        for m in re.finditer(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", s):
            idx_links.append(m.group(1).strip())

print("实际被扫描的文件数：%d" % scanned)
print("index.md 中检出的链接：%d 条" % len(idx_links))
missing = [t for t in idx_links if t not in pages]
print("index.md 中指向不存在页面的链接：%d" % len(set(missing)))
for t in sorted(set(missing))[:10]:
    print("   ", t)
