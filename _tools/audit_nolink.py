"""统计 112 篇无概念链接文档页的分布，供决定是否补概念页。"""
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
    if "[[" in seg:
        continue
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    sp = m.group(1).strip() if m else ""
    reason = "其他"
    if "已屏蔽" in seg:
        reason = "凭据屏蔽页"
    elif "无独立概念页" in seg:
        reason = "无独立概念页"
    elif "未挂接" in seg:
        reason = "原文为截图、无可抽文字"
    rows.append((f, sp, reason))

print("无概念链接文档页：%d\n" % len(rows))
print("=== 按原因 ===")
for k, v in collections.Counter(r[2] for r in rows).most_common():
    print("  %-24s %d" % (k, v))

print("\n=== 按原文目录 ===")
def top(sp):
    parts = sp.replace("\\", "/").split("/")
    for i, p in enumerate(parts):
        if p in ("personal-assets",):
            return parts[i + 1] if i + 1 < len(parts) else "(根)"
    return "(未知)"

for k, v in collections.Counter(top(r[1]) for r in rows).most_common():
    print("  %-24s %d" % (k, v))

print("\n=== 「无独立概念页」的明细 ===")
for f, sp, why in rows:
    if why == "无独立概念页":
        print("  %-42s %s" % (f[:-3][:40], sp.replace("raw/docs/personal-assets/", "")))
