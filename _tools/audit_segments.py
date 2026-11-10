import io, os, re

KB = r"D:/workspace/ai_kb_base/second-brain"
BASE = ["是什么", "怎样理解 · 为什么", "有什么性质", "怎么用", "关系", "常见误区", "出处"]
DIRS = [("entities", "entity"), ("methods", "method"), ("metrics", "metric")]

print("=== 非概念节点页的七段完整度 ===\n")
bad = []
for d, tp in DIRS:
    p = os.path.join(KB, "wiki", d)
    print("--- %s (%s) ---" % (d, tp))
    for f in sorted(os.listdir(p)):
        if not f.endswith(".md"):
            continue
        s = io.open(os.path.join(p, f), encoding="utf-8").read()
        segs = set(x.strip() for x in re.findall(r"^## (.+)$", s, re.M))
        miss = [b for b in BASE if b not in segs]
        extra = [x for x in segs if x not in BASE]
        flag = "OK" if not miss else "缺 %d" % len(miss)
        print("  %-14s %-8s %s" % (f[:-3], flag, ("缺：" + "、".join(miss)) if miss else ""))
        if miss:
            bad.append((d, f[:-3], miss))
        if extra:
            print("                额外段：" + "、".join(sorted(extra)))
    print()

print("=== 汇总 ===")
print("七段不全的页：%d" % len(bad))
for d, n, m in bad:
    print("  %s/%s 缺 %s" % (d, n, "、".join(m)))
