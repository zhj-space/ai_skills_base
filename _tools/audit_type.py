import io
import os
import re
import collections

KB = r"D:/workspace/ai_kb_base/second-brain"
DIRS = {"concepts": "wiki/概念", "summaries": "wiki/文档", "analysis": "wiki/沉淀", "模板": "wiki/_模板"}

pairs = collections.Counter()
rows = []
for label, sub in DIRS.items():
    p = os.path.join(KB, sub)
    if not os.path.isdir(p):
        continue
    for f in sorted(os.listdir(p)):
        if not f.endswith(".md"):
            continue
        s = io.open(os.path.join(p, f), encoding="utf-8").read()
        t = re.search(r"^type:[ \t]*(\S+)", s, re.M)
        et = re.search(r"^entity_type:[ \t]*(\S+)", s, re.M)
        tv = t.group(1) if t else "(无 type)"
        ev = et.group(1) if et else "—"
        pairs[(label, tv, ev)] += 1
        if label == "concepts" and tv == "concept" and ev in ("实体", "方法", "指标"):
            rows.append((f[:-3], ev))

print("=== 目录 × type × entity_type ===")
print("%-6s %-12s %-10s %s" % ("目录", "type", "entity_type", "篇数"))
for (d, tv, ev), n in sorted(pairs.items()):
    print("%-6s %-12s %-10s %3d" % (d, tv, ev or "—", n))

print("\n=== 「type: node」但本体类是实体/方法/指标的页 ===")
for n, ev in rows:
    print("   %-16s entity_type = %s" % (n, ev))
print("   共 %d 页" % len(rows))

# 脚本里怎么用 type
T = r"D:/workspace/ai_kb_base/_tools"
use = []
for f in sorted(os.listdir(T)):
    if not f.endswith(".py"):
        continue
    s = io.open(os.path.join(T, f), encoding="utf-8").read()
    if re.search(r'"type"|type:|\\\\btype\\\\b', s) and "concept" in s:
        use.append(f)
print("\n=== 工具脚本里同时出现 type 与 concept 的 ===")
print("   " + "、".join(use) if use else "   无")
