import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
WIKI = os.path.join(KB, "wiki")


def mds(sub):
    p = os.path.join(WIKI, sub)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []


def read(sub, fn):
    return io.open(os.path.join(WIKI, sub, fn), encoding="utf-8").read()


D = mds("summaries")
SP = re.compile(r"^source_path:[ \t]*(.+)$", re.M)

groups = collections.defaultdict(list)
for fn in D:
    s = read("summaries", fn)
    if "## 涉及概念" not in s:
        continue
    seg = s.split("## 涉及概念")[1].split("\n## ")[0]
    if "[[" in seg:
        continue
    m = SP.search(s)
    src = m.group(1).strip().strip('"') if m else "?"
    dom = src.replace("raw/docs/personal-assets/", "").split("/")[0]
    sub = "/".join(src.replace("raw/docs/personal-assets/", "").split("/")[1:2])
    groups[dom].append((fn[:-3], sub, seg.strip()[:16], s))

for dom in sorted(groups, key=lambda d: -len(groups[d])):
    items = groups[dom]
    if dom in ("android",):
        print("\n### %s（%d 篇，先略）" % (dom, len(items)))
        continue
    print("\n### %s（%d 篇）" % (dom, len(items)))
    for t, sub, seg, s in sorted(items):
        hits = re.findall(r"`(high|medium|low)`", s)
        print("   %-46s %-18s %s%s" % (t[:44], sub, seg[:12], "" if hits else " [无断言]"))
