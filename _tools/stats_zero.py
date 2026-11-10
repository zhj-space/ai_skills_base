# -*- coding: utf-8 -*-
"""统计未编译 source 的字数分布（0 字 vs 1-59 字），用于判断是否为转换失败"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)
RE_WC = re.compile(r"^word_count:\s*(\d+)", re.M)

cov = set()
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = RE_SP.search(s)
    if m:
        cov.add(m.group(1).strip().strip('"'))

zero, tiny = [], []
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, KB).replace(os.sep, "/")
        if rel in cov:
            continue
        s = io.open(p, encoding="utf-8").read()
        m = RE_WC.search(s)
        w = int(m.group(1)) if m else -1
        short = rel.replace("raw/docs/personal-assets/", "")
        if w == 0:
            zero.append(short)
        elif w > 0:
            tiny.append((w, short))

print("0 字（可能转换失败或纯图无文字）：%d" % len(zero))
print("1-59 字（有少量文字）：%d" % len(tiny))
print("\n=== 0 字清单 ===")
for x in sorted(zero):
    print("   ", x)
print("\n=== 1-59 字清单 ===")
for w, x in sorted(tiny):
    print("   %3d 字  %s" % (w, x))
