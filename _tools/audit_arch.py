import io, os, re, json, collections
KB = r"D:/workspace/ai_kb_base/second-brain"

def md(d):
    p = os.path.join(KB, d)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []

C, D, G = md("wiki/概念"), md("wiki/文档"), md("wiki/沉淀")
T = md("wiki/_模板")
BLOCK = [f for f in D if "凭据已屏蔽" in f]
SRC = []
for r, _, fs in os.walk(os.path.join(KB, "raw")):
    SRC += [os.path.join(r, f) for f in fs if f.endswith(".md")]

print("=== 各层规模 ===")
print("sources 原文      %3d" % len(SRC))
print("  其中图片类(? )   —")
print("文档页            %3d（含 %d 篇凭据屏蔽页）" % (len(D), len(BLOCK)))
print("概念页            %3d" % len(C))
print("沉淀页            %3d" % len(G))
print("模板              %3d" % len(T))
print("wiki 合计         %3d" % (len(D)+len(C)+len(G)+len(T)))

# source 覆盖
RE = re.compile(r"^source_path:/s*(.+)$", re.M)
cov = set()
for fn in D:
    s = io.open(os.path.join(KB, "wiki/文档", fn), encoding="utf-8").read()
    m = RE.search(s)
    if m:
        cov.add(m.group(1).strip().strip('"').replace("\\", "/"))
allsrc = set(os.path.relpath(p, KB).replace(os.sep, "/") for p in SRC)
print("\n=== 覆盖率 ===")
print("有文档页的原文    %3d / %d = %.1f%%" % (len(cov & allsrc), len(allsrc), len(cov & allsrc)*100.0/len(allsrc)))
un = sorted(allsrc - cov)
print("无页原文          %3d" % len(un))
for x in un[:14]:
    print("   " + x.replace("raw/docs/personal-assets/", ""))

# 概念页出链与入链
print("\n=== 概念页出链 top / 入链 ===")
link = collections.Counter()
outs = {}
for fn in C + G + D:
    d = "wiki/概念" if fn in C else ("wiki/沉淀" if fn in G else "wiki/文档")
    s = io.open(os.path.join(KB, d, fn), encoding="utf-8").read()
    tgt = set(re.findall(r"\[\[([^\]|#]+)", s))
    outs[fn[:-3]] = tgt
    for t in tgt:
        link[t] += 1
for name, n in link.most_common(8):
    print("   %-28s 入链 %3d" % (name, n))
print("   零入链页：" + ", ".join(n for n in outs if link[n] == 0)[:120])

# index / 主题地图 覆盖
idx = io.open(os.path.join(KB, "index.md"), encoding="utf-8").read()
tm = io.open(os.path.join(KB, "wiki/topic-map.md"), encoding="utf-8").read()
def stems(files): return set(f[:-3] for f in files)
def linked(s): return set(re.findall(r"\[\[([^\]|#]+)", s))
print("\n=== 索引覆盖 ===")
for label, files, txt in (("文档页", D, idx), ("概念页", C, idx), ("沉淀页", G, idx)):
    st = stems(files); lk = linked(txt)
    miss = st - lk
    print("%-6s 收录 %3d / %d  缺 %d" % (label, len(st & lk), len(st), len(miss)))
    if miss and len(miss) <= 6: print("        缺：" + ", ".join(sorted(miss)))
stc = stems(C); lkt = linked(tm)
print("主题地图 收录概念 %3d / %d  缺 %d" % (len(stc & lkt), len(stc), len(stc - lkt)))
if stc - lkt: print("        缺：" + ", ".join(sorted(stc - lkt))[:200])
