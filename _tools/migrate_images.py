# -*- coding: utf-8 -*-
"""把 sources 下所有 images/ 图片统一迁到 attachments/youdao/ 并改写引用"""
import os, re, io, hashlib, shutil, json

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DST = os.path.join(KB, "attachments", "youdao")
for sub in ("youdao", "web", "video", "pdf"):
    os.makedirs(os.path.join(KB, "attachments", sub), exist_ok=True)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

records = []
for root, dirs, files in os.walk(SRC):
    if os.path.basename(root) != "images":
        continue
    for fn in files:
        p = os.path.join(root, fn)
        records.append((os.path.dirname(root), fn, p, md5(p)))

print("发现图片 %d 张，分布 %d 个 images 目录" % (len(records), len({r[0] for r in records})))

by_hash = {}
used_names = {}
mapping = {}
copied = 0
dedup = 0

for notedir, fn, path, h in sorted(records, key=lambda x: (x[0], x[1])):
    if h in by_hash:
        mapping[(notedir, fn)] = by_hash[h]
        dedup += 1
        continue
    stem, ext = os.path.splitext(fn)
    newname = fn
    if newname in used_names and used_names[newname] != h:
        i = 2
        while True:
            cand = "%s_%d%s" % (stem, i, ext)
            if cand not in used_names:
                newname = cand
                break
            i += 1
    used_names[newname] = h
    by_hash[h] = newname
    mapping[(notedir, fn)] = newname
    shutil.copy2(path, os.path.join(DST, newname))
    copied += 1

print("落盘 %d 张（去重省 %d 张），唯一名 %d 个" % (copied, dedup, len(used_names)))

changed = miss = repl_total = 0
for root, _, files in os.walk(SRC):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        s = io.open(p, encoding="utf-8").read()
        if "(./images/" not in s and "](images/" not in s:
            continue
        hits = [0]
        misslist = []

        def repl(m, root=root, hits=hits, misslist=misslist):
            alt, name = m.group(1), m.group(2)
            key = (root, name)
            if key in mapping:
                hits[0] += 1
                return "![%s](attachments/youdao/%s)" % (alt, mapping[key])
            misslist.append(name)
            return m.group(0)

        s2 = re.sub(r"!\[([^\]]*)\]\(\.?/?images/([^)]+)\)", repl, s)
        if hits[0]:
            io.open(p, "w", encoding="utf-8", newline="").write(s2)
            changed += 1
            repl_total += hits[0]
        if misslist:
            miss += len(misslist)
            print("  [未匹配] %s -> %s" % (os.path.relpath(p, KB), misslist[:3]))

print("改写 %d 篇 / %d 处引用，未匹配 %d 处" % (changed, repl_total, miss))

io.open(os.path.join(KB, "_tools", "img_mapping.json"), "w", encoding="utf-8").write(
    json.dumps({"%s|%s" % k: v for k, v in mapping.items()}, ensure_ascii=False, indent=1))
print("映射表已存 _tools/img_mapping.json")
