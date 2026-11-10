import io
import os
import re
import collections

DD = r"D:/workspace/ai_kb_base/second-brain/wiki/文档"
D = sorted(f for f in os.listdir(DD) if f.endswith(".md"))

cat = collections.Counter()
for f in D:
    s = io.open(os.path.join(DD, f), encoding="utf-8").read()
    seg = s.split("## 涉及概念", 1)[1].split("\n## ", 1)[0] if "## 涉及概念" in s else ""
    if "[[" in seg:
        cat["有概念链接"] += 1
    elif "已屏蔽" in seg:
        cat["凭据屏蔽页"] += 1
    elif "无可提取文字" in seg:
        cat["纯图/无文字"] += 1
    elif "无独立概念页" in seg:
        cat["上游无概念页"] += 1
    elif "无足够信息" in seg:
        cat["信息不足"] += 1
    else:
        cat["其他"] += 1

print("=== 306 篇文档页的分类 ===")
for k, v in cat.most_common():
    print("   %-12s %3d" % (k, v))
print("   合计 %d" % sum(cat.values()))

# 「上游无概念页」里，按领域统计（这些是建概念页能救的）
g = collections.Counter()
SP = re.compile(r"^source_path:[ \t]*(.+)$", re.M)
for f in D:
    s = io.open(os.path.join(DD, f), encoding="utf-8").read()
    seg = s.split("## 涉及概念", 1)[1].split("\n## ", 1)[0] if "## 涉及概念" in s else ""
    if "无独立概念页" not in seg:
        continue
    m = SP.search(s)
    src = m.group(1).strip().strip('"') if m else "?"
    dom = src.replace("raw/docs/personal-assets/", "").split("/")[0]
    g[dom] += 1
print("\n=== 上游无概念页的分布（建页可救）===")
for k, v in g.most_common():
    print("   %-10s %3d" % (k, v))
