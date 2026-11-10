# -*- coding: utf-8 -*-
"""核查沉淀层（修正版）：章节名与 based_on 格式按实际模板"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
D = os.path.join(KB, "wiki", "analysis")
IDX = os.path.join(D, "digest-index.md")

idx = io.open(IDX, encoding="utf-8").read()
linked = set(re.findall(r"\[\[([^\]|]+)", idx))

files = [f for f in sorted(os.listdir(D)) if f.endswith(".md") and not f.startswith("沉淀索引")]
print("沉淀页：%d 篇\n" % len(files))

SECTIONS = ["问题是什么", "怎样理解问题", "如何解决", "如何做的更好", "变更记录"]

print("%-40s %-5s %-5s %-5s %s" % ("文件", "基于", "出链", "索引", "结构"))
print("-" * 88)
ok = 0
for fn in files:
    stem = fn[:-3]
    s = io.open(os.path.join(D, fn), encoding="utf-8").read()
    based = re.search(r"^based_on:\s*\[(.+?)\]", s, re.M)
    nb = len([x for x in based.group(1).split(",") if x.strip()]) if based else 0
    links = len(re.findall(r"\[\[", s))
    inidx = "✓" if stem in linked else "✗"
    secs = sum(1 for x in SECTIONS if ("## " + x) in s)
    if secs == len(SECTIONS) and inidx == "✓":
        ok += 1
    print("%-40s %-5d %-5d %-5s %d/%d" % (stem, nb, links, inidx, secs, len(SECTIONS)))

print("\n完全合规：%d / %d" % (ok, len(files)))

# based_on 指向的概念页是否都存在
concepts = {f[:-3] for f in os.listdir(os.path.join(KB, "wiki", "concepts")) if f.endswith(".md")}
miss = set()
for fn in files:
    s = io.open(os.path.join(D, fn), encoding="utf-8").read()
    m = re.search(r"^based_on:\s*\[(.+?)\]", s, re.M)
    if m:
        for x in [y.strip() for y in m.group(1).split(",")]:
            if x and x not in concepts:
                miss.add((fn[:-3], x))
print("based_on 指向不存在概念页：%d" % len(miss))
for a, b in sorted(miss):
    print("   %s -> %s" % (a, b))
