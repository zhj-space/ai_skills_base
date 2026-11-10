# -*- coding: utf-8 -*-
"""核查沉淀层：数量、结构完整性、索引登记、出链"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
D = os.path.join(KB, "wiki", "analysis")
IDX = os.path.join(D, "digest-index.md")

idx = io.open(IDX, encoding="utf-8").read()
linked = set(re.findall(r"\[\[([^\]|]+)", idx))

files = [f for f in sorted(os.listdir(D)) if f.endswith(".md") and not f.startswith("沉淀索引")]
print("沉淀页：%d 篇\n" % len(files))

SECTIONS = ["问题是什么", "怎样理解问题", "结论", "边界在哪"]
print("%-42s %-6s %-6s %-8s %s" % ("文件", "基于", "出链", "索引", "结构"))
print("-" * 92)
for fn in files:
    stem = fn[:-3]
    s = io.open(os.path.join(D, fn), encoding="utf-8").read()
    based = re.search(r"^based_on:\s*(.+)$", s, re.M)
    nb = len(re.findall(r"\[\[", based.group(1))) if based else 0
    links = len(re.findall(r"\[\[", s))
    inidx = "✓" if stem in linked else "✗"
    secs = sum(1 for x in SECTIONS if x in s)
    print("%-42s %-6s %-6s %-8s %d/4" % (stem, nb, links, inidx, secs))

# 索引里登记了但文件不存在的
missing = [x for x in linked if x.startswith("2026-") and x not in [f[:-3] for f in files]]
print("\n索引登记但文件缺失：%d" % len(missing))
for x in missing:
    print("   ", x)
