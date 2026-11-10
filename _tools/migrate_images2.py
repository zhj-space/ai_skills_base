# -*- coding: utf-8 -*-
"""
重跑图片迁移：按 sources 的来源分层，落到 attachments/{docs,web,video,other}/
步骤：
  1. 从备份恢复 md（引用回到 ./images/）
  2. 清空 attachments 重建四分类
  3. 按 md5 去重复制到 attachments/docs/
  4. 改写引用
  5. 保存映射表（立刻落盘，防中断）
"""
import os, re, io, hashlib, shutil, json

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
BAK = r"D:/workspace/ai_kb_base/_backup_图片迁移前_20261106/sources_文档"
ATT = os.path.join(KB, "attachments")
DST = os.path.join(ATT, "docs")

# ---- 1. 恢复 md ----
n_md = 0
for root, _, files in os.walk(BAK):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        rel = os.path.relpath(os.path.join(root, fn), BAK)
        dst = os.path.join(SRC, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(root, fn), dst)
        n_md += 1
print("[1] 恢复 md %d 篇" % n_md)

# ---- 2. 重建 attachments ----
if os.path.exists(ATT):
    shutil.rmtree(ATT)
for sub in ("docs", "web", "video", "other"):
    os.makedirs(os.path.join(ATT, sub), exist_ok=True)
print("[2] 重建 attachments/{docs,web,video,other}")

# ---- 3. 去重复制 ----
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

records = []
for root, _, files in os.walk(SRC):
    if os.path.basename(root) != "images":
        continue
    for fn in files:
        p = os.path.join(root, fn)
        records.append((os.path.dirname(root), fn, p, md5(p)))

by_hash, used, mapping = {}, {}, {}
copied = dedup = 0
for notedir, fn, path, h in sorted(records, key=lambda x: (x[0], x[1])):
    if h in by_hash:
        mapping["%s|%s" % (notedir, fn)] = by_hash[h]
        dedup += 1
        continue
    stem, ext = os.path.splitext(fn)
    name = fn
    if name in used and used[name] != h:
        i = 2
        while "%s_%d%s" % (stem, i, ext) in used:
            i += 1
        name = "%s_%d%s" % (stem, i, ext)
    used[name] = h
    by_hash[h] = name
    mapping["%s|%s" % (notedir, fn)] = name
    shutil.copy2(path, os.path.join(DST, name))
    copied += 1

io.open(r"D:/workspace/ai_kb_base/_tools/img_mapping.json", "w", encoding="utf-8").write(
    json.dumps(mapping, ensure_ascii=False, indent=1))
print("[3] 落盘 %d 张（去重省 %d），唯一名 %d，映射表已存" % (copied, dedup, len(used)))

# ---- 4. 改写引用 ----
changed = miss = total = 0
for root, _, files in os.walk(SRC):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        s = io.open(p, encoding="utf-8").read()
        if "images/" not in s:
            continue
        hits = [0]

        def repl(m, root=root, hits=hits):
            alt, name = m.group(1), m.group(2)
            key = "%s|%s" % (root, name)
            if key in mapping:
                hits[0] += 1
                return "![%s](attachments/docs/%s)" % (alt, mapping[key])
            miss += 1
            print("  [未匹配] %s -> %s" % (os.path.relpath(p, KB), name))
            return m.group(0)

        s2 = re.sub(r"!\[([^\]]*)\]\(\.?/?images/([^)]+)\)", repl, s)
        if hits[0]:
            io.open(p, "w", encoding="utf-8", newline="").write(s2)
            changed += 1
            total += hits[0]

print("[4] 改写 %d 篇 / %d 处引用，未匹配 %d 处" % (changed, total, miss))

# ---- 5. 删除空 images 目录 ----
removed = 0
for root, dirs, files in os.walk(SRC, topdown=False):
    if os.path.basename(root) == "images" and not os.listdir(root):
        os.rmdir(root)
        removed += 1
print("[5] 删除空 images 目录 %d 个" % removed)
