import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
WIKI = os.path.join(KB, "wiki")


def mds(sub):
    p = os.path.join(WIKI, sub)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []


def read(sub, fn):
    return io.open(os.path.join(WIKI, sub, fn), encoding="utf-8").read()


D, C = mds("summaries"), mds("concepts")
print("=== 现有 %d 个概念页 ===" % len(C))
print("、".join(sorted(f[:-3] for f in C)))

print("\n=== A. 写了概念名但未加双括号的页 ===")
loose = []
for fn in D:
    s = read("summaries", fn)
    if "## 涉及概念" not in s:
        continue
    seg = s.split("## 涉及概念")[1].split("\n## ")[0]
    if "[[" in seg:
        continue
    body = seg.strip()
    if body.startswith("（"):
        continue
    loose.append((fn, body.replace("\n", " ")[:70]))
for fn, b in loose:
    print("   %-52s %s" % (fn[:-3][:50], b))

print("\n=== B. 缺「涉及概念」节的页 ===")
for fn in D:
    if "## 涉及概念" not in read("summaries", fn):
        print("   " + fn)

print("\n=== C. 悬空链接目标核实 ===")
cset = set(f[:-3] for f in C)
allsrc = set()
for r, _, fs in os.walk(os.path.join(KB, "raw")):
    for f in fs:
        if f.endswith(".md"):
            allsrc.add(f[:-3])
for t in ("内存管理", "类与对象"):
    print("   %-10s 是概念页=%s 原文中有同名文件=%s" % (t, t in cset, t in allsrc))
    hits = [f for f in D if "[[" + t + "]]" in read("summaries", f)]
    print("        引用页：" + "、".join(h[:-3][:26] for h in hits))

print("\n=== D. 「无独立概念页」类：按来源目录聚合 ===")
grp = collections.Counter()
for fn in D:
    s = read("summaries", fn)
    if "## 涉及概念" not in s:
        continue
    seg = s.split("## 涉及概念")[1].split("\n## ")[0]
    if "[[" in seg and "无独立概念页" not in seg:
        continue
    if "无独立概念页" not in seg:
        continue
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    src = m.group(1).strip().strip('"') if m else "?"
    parts = src.split("/")
    key = "/".join(parts[4:6]) if len(parts) > 5 else src
    grp[key] += 1
for k, v in grp.most_common():
    print("   %-40s %3d" % (k, v))

print("\n=== E. 「未挂接」类：按来源目录聚合 ===")
grp2 = collections.Counter()
for fn in D:
    s = read("summaries", fn)
    if "## 涉及概念" not in s:
        continue
    seg = s.split("## 涉及概念")[1].split("\n## ")[0]
    if "未挂接" not in seg:
        continue
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    src = m.group(1).strip().strip('"') if m else "?"
    parts = src.split("/")
    key = "/".join(parts[4:6]) if len(parts) > 5 else src
    grp2[key] += 1
for k, v in grp2.most_common(12):
    print("   %-40s %3d" % (k, v))
