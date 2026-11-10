import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
WIKI = os.path.join(KB, "wiki")


def mds(sub):
    p = os.path.join(WIKI, sub)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []


C = mds("concepts")
D = mds("summaries")
G = mds("analysis")
SRC = []
for r, _, fs in os.walk(os.path.join(KB, "raw")):
    for f in fs:
        if f.endswith(".md"):
            SRC.append(os.path.join(r, f))

SP = re.compile(r"^source_path:[ \t]*(.+)$", re.M)


def read(sub, fn):
    return io.open(os.path.join(WIKI, sub, fn), encoding="utf-8").read()


cov = {}
for fn in D:
    m = SP.search(read("summaries", fn))
    if m:
        cov[m.group(1).strip().strip('"').replace("\\", "/")] = fn

allsrc = {}
for p in SRC:
    rel = os.path.relpath(p, KB).replace(os.sep, "/")
    allsrc[rel] = p

hit = set(cov) & set(allsrc)
print("=== 覆盖率 ===")
print("source_path 可解析    %d / %d 篇文档页" % (len(cov), len(D)))
print("命中真实原文          %d / %d = %.1f%%" % (len(hit), len(allsrc), len(hit) * 100.0 / len(allsrc)))
un = sorted(set(allsrc) - set(cov))
print("无文档页的原文        %d" % len(un))
for x in un:
    print("   " + x.replace("raw/docs/personal-assets/", ""))

print("\n=== 按一级领域分布（sources）===")
cnt = collections.Counter()
for rel in allsrc:
    parts = rel.split("/")
    key = parts[3] if len(parts) > 3 else "(根)"
    cnt[key] += 1
covered = collections.Counter()
for rel in hit:
    parts = rel.split("/")
    covered[parts[3] if len(parts) > 3 else "(根)"] += 1
print("%-14s %6s %6s %6s" % ("领域", "原文", "有页", "覆盖"))
for k, v in cnt.most_common():
    print("%-14s %6d %6d %5.0f%%" % (k, v, covered.get(k, 0), covered.get(k, 0) * 100.0 / v))

print("\n=== 文档页信息密度 ===")
sizes = []
for fn in D:
    s = read("summaries", fn)
    nc = len(re.findall(r"`(high|medium|low)`", s))
    sizes.append((nc, len(s), fn))
zero = [x for x in sizes if x[0] == 0]
print("无断言的文档页        %d / %d（%.0f%%）" % (len(zero), len(D), len(zero) * 100.0 / len(D)))
print("断言总数              %d" % sum(x[0] for x in sizes))
avg = sum(x[0] for x in sizes) / float(len(sizes))
print("平均每页断言          %.1f 条" % avg)
print("页内字节中位数        %d" % sorted(x[1] for x in sizes)[len(sizes) // 2])

print("\n=== 概念页规模 ===")
cs = []
for fn in C:
    s = read("concepts", fn)
    cs.append((s.count("\n") + 1, len(s), fn[:-3]))
cs.sort()
print("概念页 %d 个，行数 最小 %d / 中位 %d / 最大 %d" % (len(cs), cs[0][0], cs[len(cs) // 2][0], cs[-1][0]))
print("最薄的 5 页：")
for l, b, n in cs[:5]:
    print("   %-28s %3d 行" % (n, l))

print("\n=== 概念网络（仅概念页之间）===")
cset = set(f[:-3] for f in C)
outs = {}
indeg = collections.Counter()
for fn in C:
    tgt = set(re.findall(r"\[\[([^\]|#]+)", read("concepts", fn))) & cset
    outs[fn[:-3]] = tgt
    for t in tgt:
        indeg[t] += 1
iso = [n for n in cset if indeg[n] == 0]
print("概念页间有向边        %d" % sum(len(v) for v in outs.values()))
print("平均出链              %.1f" % (sum(len(v) for v in outs.values()) / float(len(cset))))
print("零入链概念页          %d：%s" % (len(iso), ", ".join(sorted(iso))[:90]))
print("枢纽概念（入链 top6）：")
for n, k in indeg.most_common(6):
    print("   %-28s %3d" % (n, k))

print("\n=== 沉淀层 ===")
for fn in sorted(G):
    s = read("analysis", fn)
    bo = re.search(r"^based_on:[ \t]*(.+)$", s, re.M)
    print("   %-46s %3d 行  based_on %s" % (fn[:-3][:44], s.count("\n") + 1, "有" if bo else "无"))
