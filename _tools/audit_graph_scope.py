import io, os, re, json

KB = r"D:/workspace/ai_kb_base/second-brain"
GROUPS = {
    "concepts": "concept", "entities": "entity", "methods": "method",
    "metrics": "metric", "analysis": "digest/index", "summaries": "doc",
}

print("=== 各目录页面数（当前 filter 是否包含）===")
IN_FILTER = {"concepts", "entities", "methods", "metrics", "analysis"}
total_in = 0
for d, t in GROUPS.items():
    p = os.path.join(KB, "wiki", d)
    n = len([f for f in os.listdir(p) if f.endswith(".md")]) if os.path.isdir(p) else 0
    mark = "在" if d in IN_FILTER else "不在"
    if d in IN_FILTER:
        total_in += n
    print("  wiki/%-10s %3d 页  %-12s %s" % (d, n, t, mark))
print("  当前图谱节点 = %d" % total_in)

# 度数统计：当前在 filter 内的节点里，有多少是孤立/低度
NODE_DIRS = ["concepts", "entities", "methods", "metrics"]
nodes = set()
for d in NODE_DIRS:
    p = os.path.join(KB, "wiki", d)
    for f in os.listdir(p):
        if f.endswith(".md"):
            nodes.add(f[:-3])

deg = {n: 0 for n in nodes}
for d in NODE_DIRS:
    p = os.path.join(KB, "wiki", d)
    for f in os.listdir(p):
        if not f.endswith(".md"):
            continue
        s = io.open(os.path.join(p, f), encoding="utf-8").read()
        seg = s.split("## 关系")[1].split("\n## ")[0] if "## 关系" in s else ""
        for tgt in re.findall(r"\[\[([^\]|#]+)", seg):
            tgt = tgt.strip()
            if tgt in deg:
                deg[tgt] += 1
            if f[:-3] in deg:
                deg[f[:-3]] += 1

zero = [n for n, v in deg.items() if v == 0]
print("\n知识节点中度数为 0（孤立）的：%d 个" % len(zero))
if zero:
    print("  " + "、".join(sorted(zero)))

# 沉淀页是否都有基于节点
ad = os.path.join(KB, "wiki", "analysis")
print("\n=== analysis 目录明细 ===")
for f in sorted(os.listdir(ad)):
    if f.endswith(".md"):
        print("  " + f)
