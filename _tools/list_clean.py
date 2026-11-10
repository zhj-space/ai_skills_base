# -*- coding: utf-8 -*-
"""列出指定条目中所有「不含 ** 标记且长度足够」的句子，供挑选证据"""
import io, re

SRC = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/数学/同济版高数知识点梳理.md"
lines = io.open(SRC, encoding="utf-8").read().split("\n")

# 找条目起始行
starts = {}
for i, ln in enumerate(lines):
    m = re.match(r"^(\d+\.\d+)([^\s].{1,40})$", ln.strip())
    if m:
        starts[m.group(1)] = i
order = sorted(starts.items(), key=lambda x: x[1])
rng = {}
for k, (no, li) in enumerate(order):
    end = order[k+1][1] if k+1 < len(order) else len(lines)
    for j in range(li+1, end):
        if lines[j].startswith("## "):
            end = j; break
    rng[no] = (li+1, end)

TARGETS = ["1.2","2.4","3.1","3.5","3.6","4.1","4.2","4.3","5.3","5.4","6.1","7.1","7.2","7.3","7.4",
           "8.1","8.2","8.3","9.1","9.3","9.5","9.6","10.1","10.2","10.3","11.4","11.5","11.6","12.1","12.2","12.3"]

for no in TARGETS:
    lo, hi = rng[no]
    print("="*62)
    print("# %s" % no)
    for ln in lines[lo:hi]:
        t = ln.strip().lstrip("-").strip()
        if not t or "*" in t:
            continue
        if len(re.sub(r"\s+", "", t)) < 14:
            continue
        print("   " + t[:110])
