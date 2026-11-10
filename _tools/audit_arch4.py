import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
WIKI = os.path.join(KB, "wiki")


def mds(sub):
    p = os.path.join(WIKI, sub)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []


def read(sub, fn):
    return io.open(os.path.join(WIKI, sub, fn), encoding="utf-8").read()


D, C = mds("summaries"), mds("concepts")

print("=== 文档页断言条数分布 ===")
cnt = collections.Counter()
rows = []
for fn in D:
    s = read("summaries", fn)
    n = len(re.findall(r"`(high|medium|low)`", s))
    rows.append((n, fn))
    if n == 0:
        cnt["0"] += 1
    elif n <= 2:
        cnt["1-2"] += 1
    elif n <= 4:
        cnt["3-4"] += 1
    elif n <= 9:
        cnt["5-9"] += 1
    else:
        cnt["10+"] += 1
for k in ("0", "1-2", "3-4", "5-9", "10+"):
    print("   %-4s %3d 篇" % (k, cnt[k]))
print("   断言总数 %d，中位数 %d 条/页" % (sum(x[0] for x in rows), sorted(x[0] for x in rows)[len(rows) // 2]))
print("   断言最多的 5 页：")
for n, fn in sorted(rows, reverse=True)[:5]:
    print("      %-44s %3d" % (fn[:-3][:42], n))

print("\n=== 疑似重复文档页（同 source 或多页同名源）===")
SP = re.compile(r"^source_path:[ \t]*(.+)$", re.M)
bysrc = collections.defaultdict(list)
for fn in D:
    m = SP.search(read("summaries", fn))
    if m:
        bysrc[m.group(1).strip().strip('"')].append(fn)
dup = {k: v for k, v in bysrc.items() if len(v) > 1}
print("同一 source 对应多页：%d 组" % len(dup))
for k, v in list(dup.items())[:5]:
    print("   %s -> %s" % (k.split("/")[-1], v))

print("\n=== 概念页出链是否指向存在页 ===")
cset = set(f[:-3] for f in C)
allpages = cset | set(f[:-3] for f in D) | set(f[:-3] for f in mds("analysis"))
bad = collections.Counter()
for fn in C:
    for t in re.findall(r"\[\[([^\]|#]+)", read("concepts", fn)):
        if t not in allpages:
            bad[t] += 1
print("概念页中的无效双括号：%d 个" % len(bad))
for k, v in bad.most_common(6):
    print("   %-22s %d 次" % (k, v))

print("\n=== 文档页 → 概念页 反向链接 ===")
n_back = 0
for fn in D:
    s = read("summaries", fn)
    seg = s.split("## 涉及概念")[-1] if "## 涉及概念" in s else ""
    if "[[" in seg:
        n_back += 1
print("有「涉及概念」且含链接：%d / %d（%.0f%%）" % (n_back, len(D), n_back * 100.0 / len(D)))
