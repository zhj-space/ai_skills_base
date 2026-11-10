import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
WIKI = os.path.join(KB, "wiki")


def mds(sub):
    p = os.path.join(WIKI, sub)
    return [f for f in os.listdir(p) if f.endswith(".md")] if os.path.isdir(p) else []


def read(sub, fn):
    return io.open(os.path.join(WIKI, sub, fn), encoding="utf-8").read()


C, D, G = mds("concepts"), mds("summaries"), mds("analysis")

print("=== 概念页厚度分布 ===")
bins = [(0, 70), (70, 100), (100, 150), (150, 999)]
rows = []
for fn in C:
    s = read("concepts", fn)
    rows.append((s.count("\n") + 1, fn[:-3]))
for lo, hi in bins:
    sel = [r for r in rows if lo <= r[0] < hi]
    print("%3d–%3d 行：%2d 个   %s" % (lo, min(hi, 999), len(sel), ", ".join(x[1] for x in sorted(sel))[:110]))
print("合计 %d 个" % len(rows))

print("\n=== 84 篇无断言页的构成 ===")
nc = []
for fn in D:
    s = read("summaries", fn)
    if not re.search(r"`(high|medium|low)`", s):
        imgs = len(re.findall(r"!\[", s))
        nc.append((imgs, s.count("\n") + 1, fn))
img = [x for x in nc if x[0] > 0]
txt = [x for x in nc if x[0] == 0]
print("纯图片页（有图引用）  %d" % len(img))
print("短文本页（无图）      %d" % len(txt))
print("其中正文 <15 行：     %d" % sum(1 for x in txt if x[1] < 15))
print("样本（短文本）：" + ", ".join(x[2][:16] for x in txt[:5]))

print("\n=== 主题地图分组 ===")
tm = io.open(os.path.join(WIKI, "topic-map.md"), encoding="utf-8").read()
cur = None
cnt = collections.OrderedDict()
for ln in tm.split("\n"):
    if ln.startswith("## "):
        cur = ln[3:].strip()
        cnt.setdefault(cur, 0)
    elif ln.startswith("### "):
        cur = "  " + ln[4:].strip()
        cnt.setdefault(cur, 0)
    elif ln.startswith("- [[") and cur:
        cnt[cur] += 1
for k, v in cnt.items():
    if v:
        print("%-24s %2d" % (k, v))

print("\n=== 索引与文档结构 ===")
idx = io.open(os.path.join(KB, "index.md"), encoding="utf-8").read()
print("index.md             %d 行 / %d KB" % (idx.count("\n") + 1, len(idx) // 1024))
print("主题地图            %d 行" % (tm.count("\n") + 1))
for ln in idx.split("\n"):
    if ln.startswith("## "):
        print("   索引节：" + ln[3:])

print("\n=== 体积 ===")
def du(p):
    t = 0
    for r, _, fs in os.walk(p):
        for f in fs:
            try:
                t += os.path.getsize(os.path.join(r, f))
            except Exception:
                pass
    return t
for name, p in (("库本体", KB), ("raw", os.path.join(KB, "raw")),
                ("wiki", WIKI), ("attachments", os.path.join(KB, "attachments"))):
    print("%-14s %7.1f MB" % (name, du(p) / 1048576.0))
