"""精确筛出 64 篇「无独立概念页」文档页，按原文目录分组。"""
import io
import os
import re
import collections

KB = r"D:/workspace/ai_kb_base/second-brain"
DOC = os.path.join(KB, "wiki", "summaries")

rows = []
for f in sorted(os.listdir(DOC)):
    if not f.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, f), encoding="utf-8").read()
    seg = s.split("## 涉及概念")[1].split("\n## ")[0] if "## 涉及概念" in s else ""
    if "[[" in seg or "无独立概念页" not in seg:
        continue
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    sp = m.group(1).strip().replace("raw/docs/personal-assets/", "") if m else "?"
    rows.append((f[:-3], sp))


def area(sp):
    p = sp.split("/")
    return p[0] if len(p) > 1 else "(根)"


g = collections.defaultdict(list)
for name, sp in rows:
    g[area(sp)].append((name, sp))

print("「无独立概念页」共 %d 篇\n" % len(rows))
for k in sorted(g, key=lambda x: -len(g[x])):
    print("=== %-12s %d 篇 ===" % (k, len(g[k])))
    if len(g[k]) <= 14:
        for name, sp in g[k]:
            print("   %-40s %s" % (name[:38], sp))
    else:
        # 大组只看子目录分布
        sub = collections.Counter(sp.split("/")[1] if len(sp.split("/")) > 2 else "(直属)"
                                  for _, sp in g[k])
        for s2, c2 in sub.most_common():
            print("   %-16s %d 篇" % (s2, c2))
    print()
