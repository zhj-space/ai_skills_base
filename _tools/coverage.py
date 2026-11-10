# -*- coding: utf-8 -*-
"""分析 sources → wiki/文档 的编译覆盖率"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw")
DOC = os.path.join(KB, "wiki", "summaries")

# 1) wiki/文档 里的 source_path
covered = {}
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = re.search(r"^source_path:\s*(.+)$", s, re.M)
    if m:
        covered[m.group(1).strip()] = fn

print("wiki/文档 共 %d 篇，其中带 source_path 的 %d 篇" % (
    len([x for x in os.listdir(DOC) if x.endswith(".md")]), len(covered)))

# 2) sources 全量
srcs = []
for root, _, files in os.walk(SRC):
    for fn in files:
        if fn.endswith(".md"):
            p = os.path.join(root, fn)
            srcs.append(os.path.relpath(p, KB).replace("\\", "/"))

print("sources 共 %d 篇" % len(srcs))

# 3) 未编译
uncovered = [s for s in srcs if s not in covered]
print("已编译 %d 篇 / 未编译 %d 篇" % (len(srcs) - len(uncovered), len(uncovered)))

# 4) 按一级分类统计
def top(s):
    parts = s.split("/")
    # raw/docs/personal-assets/<分类>/...
    if len(parts) >= 4:
        return parts[3]
    return "(顶层)"

stat_all = collections.Counter(top(s) for s in srcs)
stat_unc = collections.Counter(top(s) for s in uncovered)

print("\n%-16s %6s %6s %6s" % ("分类", "总篇", "已编", "未编"))
print("-" * 40)
for k, n in stat_all.most_common():
    print("%-16s %6d %6d %6d" % (k, n, n - stat_unc.get(k, 0), stat_unc.get(k, 0)))

# 5) 未编译清单（按分类列出前几篇）
print("\n=== 未编译清单（每类前 3 篇）===")
by = collections.defaultdict(list)
for s in uncovered:
    by[top(s)].append(s)
for k in sorted(by, key=lambda x: -len(by[x])):
    print("\n[%s] %d 篇" % (k, len(by[k])))
    for s in by[k][:3]:
        print("   " + s)
