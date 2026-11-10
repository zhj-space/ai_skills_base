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

rows = []
for fn in D:
    s = read("summaries", fn)
    seg = s.split("## 涉及概念")[1].split("\n## ")[0] if "## 涉及概念" in s else "(无该节)"
    has = "[[" in seg
    m = SP.search(s)
    src = m.group(1).strip().strip('"') if m else "?"
    dom = src.replace("raw/docs/personal-assets/", "").split("/")[0]
    rows.append((fn, dom, has, seg.strip().replace("\n", " ")[:26], src))

cat = collections.Counter()
for fn, dom, has, seg, src in rows:
    if has:
        cat["有链接"] += 1
    elif "已屏蔽" in seg:
        cat["已屏蔽"] += 1
    elif "无可提取文字" in seg:
        cat["纯图未挂接"] += 1
    elif "无足够信息" in seg:
        cat["无足够信息"] += 1
    elif "无独立概念页" in seg:
        cat["无独立概念页"] += 1
    elif seg == "(无该节)":
        cat["缺该节"] += 1
    else:
        cat["写了名但没加括号"] += 1
for k, v in cat.most_common():
    print("%-16s %3d" % (k, v))

print("\n=== 纯图未挂接 + 无独立概念页：按领域 ===")
g = collections.Counter()
for fn, dom, has, seg, src in rows:
    if not has and ("无可提取文字" in seg or "无独立概念页" in seg):
        g[dom] += 1
for k, v in g.most_common():
    print("   %-14s %3d" % (k, v))

print("\n=== 无足够信息（%d 篇）明细 ===" % sum(1 for r in rows if "无足够信息" in r[3]))
for fn, dom, has, seg, src in rows:
    if "无足够信息" in seg:
        print("   %-16s %-46s %s" % (dom, fn[:-3][:44], seg[:24]))

print("\n=== 无独立概念页的非 android 页 ===")
for fn, dom, has, seg, src in rows:
    if "无独立概念页" in seg and dom != "android":
        print("   %-12s %-44s %s" % (dom, fn[:-3][:42], seg[:30]))

print("\n=== 写了名但没加括号（%d 篇）===" % sum(1 for r in rows if r[3] and "[[" not in r[3] and not r[3].startswith("（") and "无该节" not in r[3]))
for fn, dom, has, seg, src in rows:
    if not has and seg != "(无该节)" and not seg.startswith("（"):
        print("   %-12s %-42s %s" % (dom, fn[:-3][:40], seg))
