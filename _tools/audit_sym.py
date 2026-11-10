import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
CD = os.path.join(KB, "wiki", "concepts")
DD = os.path.join(KB, "wiki", "summaries")

C = sorted(f[:-3] for f in os.listdir(CD) if f.endswith(".md"))
D = set(f[:-3] for f in os.listdir(DD) if f.endswith(".md"))


def read(p):
    return io.open(p, encoding="utf-8").read()


def sec(s, name):
    if name not in s:
        return ""
    return s.split(name, 1)[1].split("\n## ", 1)[0]


pairs = []
for c in C:
    s = read(os.path.join(CD, c + ".md"))
    for t in re.findall(r"\[\[([^\]|#]+)", sec(s, "## 出处")):
        if t in D:
            pairs.append((c, t))

print("概念页出处指向文档页的关系：%d 条" % len(pairs))

missing = []
cur = {}
for d in D:
    s = read(os.path.join(DD, d + ".md"))
    cur[d] = set(re.findall(r"\[\[([^\]|#]+)", sec(s, "## 涉及概念")))

for c, d in pairs:
    if c not in cur[d]:
        missing.append((d, c))

print("文档页未反向挂回的概念：%d 条，涉及 %d 篇文档页" % (len(missing), len(set(x[0] for x in missing))))

g = collections.Counter(x[0] for x in missing)
print("\n=== 按文档页汇总（缺几个概念）===")
for d, n in g.most_common(30):
    cs = [c for dd, c in missing if dd == d]
    print("   %-46s +%s" % (d[:44], "、".join(cs)))
