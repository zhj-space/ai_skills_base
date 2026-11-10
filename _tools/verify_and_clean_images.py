# -*- coding: utf-8 -*-
"""校验迁移结果，并删除旧的 images 目录"""
import os, re, io, json

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOCS = os.path.join(KB, "attachments", "docs")

# 1) 映射表条数
m = json.load(io.open(r"D:/workspace/ai_kb_base/_tools/img_mapping.json", encoding="utf-8"))
print("映射表 %d 条" % len(m))

# 2) docs 落盘文件
files = set(os.listdir(DOCS))
print("attachments/docs 实体 %d 张" % len(files))

# 3) 引用校验：每个 attachments/docs/X 必须存在
bad, total = [], 0
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        s = io.open(p, encoding="utf-8").read()
        for mm in re.finditer(r"!\[[^\]]*\]\(attachments/docs/([^)]+)\)", s):
            total += 1
            if mm.group(1) not in files:
                bad.append((os.path.relpath(p, KB), mm.group(1)))

print("引用总数 %d，指向不存在文件 %d" % (total, len(bad)))
for a, b in bad[:10]:
    print("   %s -> %s" % (a, b))

# 4) 残留旧引用
left = 0
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if fn.endswith(".md"):
            s = io.open(os.path.join(root, fn), encoding="utf-8").read()
            left += len(re.findall(r"!\[[^\]]*\]\(\.?/?images/", s))
print("残留 ./images/ 引用：%d" % left)

# 5) 全部通过才删旧目录
if not bad and left == 0:
    removed_dirs = removed_files = 0
    for root, dirs, fs in os.walk(SRC, topdown=False):
        if os.path.basename(root) == "images":
            removed_files += len(os.listdir(root))
            for f in os.listdir(root):
                os.remove(os.path.join(root, f))
            os.rmdir(root)
            removed_dirs += 1
    print("\n删除旧 images 目录 %d 个 / 文件 %d 张" % (removed_dirs, removed_files))
else:
    print("\n校验未通过，暂不删除旧目录")
