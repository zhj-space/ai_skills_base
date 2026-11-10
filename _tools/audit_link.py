import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
WIKI = os.path.join(KB, "wiki")


def mds(sub):
    p = os.path.join(WIKI, sub)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []


def read(sub, fn):
    return io.open(os.path.join(WIKI, sub, fn), encoding="utf-8").read()


D, C = mds("summaries"), mds("concepts")
cset = set(f[:-3] for f in C)

forms = collections.Counter()
no_sec = []
with_link = []
for fn in D:
    s = read("summaries", fn)
    if "## 涉及概念" not in s:
        no_sec.append(fn)
        forms["无该节"] += 1
        continue
    seg = s.split("## 涉及概念")[1]
    seg = seg.split("\n## ")[0]
    lk = re.findall(r"\[\[([^\]|#]+)", seg)
    if lk:
        forms["有链接"] += 1
        with_link.append((fn, lk))
    else:
        body = re.sub(r"\s+", "", seg)
        forms["无链接: " + (body[:14] or "(空)")] += 1

print("=== 涉及概念节的形态分布（%d 篇）===" % len(D))
for k, v in forms.most_common(12):
    print("   %-24s %3d" % (k, v))
print("\n无该节的页：%d %s" % (len(no_sec), no_sec[:4]))

print("\n=== 有链接的页，链接数分布 ===")
cc = collections.Counter(len(x[1]) for x in with_link)
for k, v in sorted(cc.items()):
    print("   %d 条链接：%d 篇" % (k, v))
print("平均 %.1f 条" % (sum(len(x[1]) for x in with_link) / float(len(with_link))))

print("\n=== 链接目标是否都是现存概念页 ===")
bad = collections.Counter()
for fn, lk in with_link:
    for t in lk:
        if t not in cset:
            bad[t] += 1
print("非概念页目标的链接：%d 个" % len(bad))
for k, v in bad.most_common(10):
    print("   %-34s %d 次" % (k, v))

print("\n=== 概念页「出处/相关文档」指向文档页的情况 ===")
dset = set(f[:-3] for f in D)
n_with = 0
tot_refs = 0
for fn in C:
    s = read("concepts", fn)
    refs = [t for t in re.findall(r"\[\[([^\]|#]+)", s) if t in dset]
    if refs:
        n_with += 1
        tot_refs += len(refs)
print("有指向文档页的概念页：%d / %d" % (n_with, len(C)))
print("概念页→文档页 引用总数：%d" % tot_refs)

print("\n=== 文档页被概念页引用的数量（应有入链）===")
inb = collections.Counter()
for fn in C:
    for t in re.findall(r"\[\[([^\]|#]+)", read("concepts", fn)):
        if t in dset:
            inb[t] += 1
print("有概念页入链的文档页：%d / %d" % (len(inb), len(D)))
zero = [f[:-3] for f in D if f[:-3] not in inb]
print("无任何概念页入链：%d" % len(zero))
