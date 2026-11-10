# -*- coding: utf-8 -*-
"""区分三类未编译 source：真空（无字无图）/ 纯图（有图无字）/ 短文本"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)
RE_WC = re.compile(r"^word_count:\s*(\d+)", re.M)
RE_IMG = re.compile(r"^images:\s*(\d+)", re.M)

cov = set()
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = RE_SP.search(s)
    if m:
        cov.add(m.group(1).strip().strip('"'))

empty, pureimg, short = [], [], []
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, KB).replace(os.sep, "/")
        if rel in cov:
            continue
        s = io.open(p, encoding="utf-8").read()
        mw = RE_WC.search(s)
        mi = RE_IMG.search(s)
        w = int(mw.group(1)) if mw else -1
        n = int(mi.group(1)) if mi else 0
        short_rel = rel.replace("raw/docs/personal-assets/", "")
        if w == 0 and n == 0:
            empty.append(short_rel)
        elif w < 60:
            pureimg.append((w, n, short_rel))
        else:
            short.append((w, short_rel))

print("【A】真空笔记（0 字 0 图，疑似转换丢失）：%d" % len(empty))
for x in sorted(empty):
    print("   ", x)
print("\n【B】纯图/短文本（有图或极短）：%d" % len(pureimg))
print("\n【C】有正文但涉敏未编译：%d" % len(short))
for w, x in sorted(short, reverse=True):
    print("   %5d 字  %s" % (w, x))
