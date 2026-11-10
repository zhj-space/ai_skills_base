# -*- coding: utf-8 -*-
"""扫描全库，输出所有未处理项清单（供生成待办日志）"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)

# ---------- 1. 已编译集合 ----------
covered = set()
withheld = []
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = RE_SP.search(s)
    if m:
        covered.add(m.group(1).strip().strip('"'))
    if "凭据已屏蔽" in fn:
        withheld.append(fn[:-3])

# ---------- 2. 未编译 source ----------
pure_img, other = [], []
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, KB).replace(os.sep, "/")
        if rel in covered:
            continue
        s = io.open(p, encoding="utf-8").read()
        wc = re.search(r"^word_count:\s*(\d+)", s, re.M)
        w = int(wc.group(1)) if wc else 0
        short = rel.replace("raw/docs/personal-assets/", "")
        if w < 60:
            pure_img.append((w, short))
        else:
            other.append((w, short))

print("【1】未编译 source 共 %d 篇" % (len(pure_img) + len(other)))
print("    纯图片/无正文（<60字）：%d" % len(pure_img))
by = collections.Counter(x[1].split("/")[0] for x in pure_img)
for k, v in by.most_common():
    print("       %-12s %d" % (k, v))
print("    有正文但未编译：%d" % len(other))
for w, x in sorted(other, reverse=True):
    print("       %5d 字  %s" % (w, x))

# ---------- 3. 第三方图床死链 ----------
dead = collections.Counter()
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        s = io.open(os.path.join(root, fn), encoding="utf-8").read()
        for m in re.finditer(r"!\[[^\]]*\]\((https?://[^)]+)\)", s):
            host = re.sub(r"^https?://", "", m.group(1)).split("/")[0]
            dead[host] += 1
print("\n【2】外链图片（未本地化）：%d 个" % sum(dead.values()))
for k, v in dead.most_common():
    print("       %-30s %d" % (k, v))

# ---------- 4. 空目录 ----------
empties = []
for base in ("raw", "attachments"):
    d = os.path.join(KB, base)
    for root, dirs, fs in os.walk(d):
        if not os.listdir(root):
            empties.append(os.path.relpath(root, KB).replace(os.sep, "/"))
print("\n【3】空目录：%d 个" % len(empties))
for e in empties:
    print("       ", e)

# ---------- 5. 凭据页 ----------
print("\n【4】凭据屏蔽页：%d 篇" % len(withheld))
for x in sorted(withheld):
    print("       ", x)

# ---------- 6. 沉淀页 ----------
d = os.path.join(KB, "wiki", "analysis")
dig = [f[:-3] for f in os.listdir(d) if f.endswith(".md") and not f.startswith("沉淀索引")]
print("\n【5】沉淀页：%d 篇" % len(dig))

# ---------- 7. 概念页 / 文档页 ----------
print("\n【6】概念页 %d / 文档页 %d / 模板 %d"
      % (len(os.listdir(os.path.join(KB, "wiki", "concepts"))),
         len([f for f in os.listdir(DOC) if f.endswith(".md")]),
         len(os.listdir(os.path.join(KB, "wiki", "_templates")))))
