import io
import os
import re
import collections

CD = r"D:/workspace/ai_kb_base/second-brain/wiki/概念"
C = sorted(f[:-3] for f in os.listdir(CD) if f.endswith(".md"))

lab = collections.Counter()
for c in C:
    s = io.open(os.path.join(CD, c + ".md"), encoding="utf-8").read()
    if "## 关系" not in s:
        continue
    seg = s.split("## 关系", 1)[1].split("\n## ", 1)[0]
    for ln in seg.split("\n"):
        m = re.match(r"^-\s*([^：:]{1,10})\s*[：:]", ln.strip())
        if m:
            lab[m.group(1).strip()] += 1

print("=== 关系段标签分布（%d 条）===" % sum(lab.values()))
for k, v in lab.most_common():
    print("   %-8s %3d" % (k, v))

print("\n=== 实例 / 实例化 明细 ===")
for c in C:
    s = io.open(os.path.join(CD, c + ".md"), encoding="utf-8").read()
    if "## 关系" not in s:
        continue
    seg = s.split("## 关系", 1)[1].split("\n## ", 1)[0]
    for ln in seg.split("\n"):
        if "实例" in ln and ln.strip().startswith("- "):
            print("   %-12s %s" % (c, ln.strip()[:64]))
