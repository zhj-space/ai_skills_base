# -*- coding: utf-8 -*-
"""库健康度全面核查"""
import os, re, io, json, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
D = os.path.join(KB, "wiki", "summaries")
C = os.path.join(KB, "wiki", "concepts")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)

bad, nosp, ok = [], [], 0
for fn in sorted(os.listdir(D)):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(D, fn), encoding="utf-8").read()
    m = RE_SP.search(s)
    if not m:
        nosp.append(fn)
        continue
    sp = m.group(1).strip().strip('"')
    if os.path.exists(os.path.join(KB, sp)):
        ok += 1
    else:
        bad.append((fn, sp))

print("文档页 %d 篇：source_path 有效 %d / 指向不存在 %d / 无字段 %d"
      % (len([f for f in os.listdir(D) if f.endswith('.md')]), ok, len(bad), len(nosp)))
for a, b in bad[:8]:
    print("   [失效] %s -> %s" % (a, b))
for x in nosp[:8]:
    print("   [无字段] %s" % x)

# 概念页是否都有 出处 段
no_src = []
for fn in sorted(os.listdir(C)):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(C, fn), encoding="utf-8").read()
    if "## 出处" not in s:
        no_src.append(fn)
print("\n概念页缺「出处」段：%d" % len(no_src))
for x in no_src[:10]:
    print("   ", x)

# 概念页出链数（关系段里的双括号）
few = []
for fn in sorted(os.listdir(C)):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(C, fn), encoding="utf-8").read()
    m = re.search(r"## 关系(.*?)## ", s, re.S)
    body = m.group(1) if m else ""
    n = len(re.findall(r"\[\[", body))
    if n < 2:
        few.append((fn[:-3], n))
print("\n「关系」段出链 <2 的概念页：%d" % len(few))
for a, b in few[:10]:
    print("   %s (%d)" % (a, b))
