# -*- coding: utf-8 -*-
"""把库内图片引用从 images/ 改为 ./images/（明确表示当前文件相对路径）"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain/raw/文档"

changed = 0
total = 0
for root, _, files in os.walk(KB):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        s = io.open(p, encoding="utf-8").read()
        n = s.count("](images/")
        if n == 0:
            continue
        s2 = s.replace("](images/", "](./images/")
        io.open(p, "w", encoding="utf-8", newline="").write(s2)
        changed += 1
        total += n

print("改动文件 %d 篇，替换引用 %d 处" % (changed, total))

# 复核：确认没有遗漏，也没有把 ././ 弄出来
bad = 0
for root, _, files in os.walk(KB):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        s = io.open(os.path.join(root, fn), encoding="utf-8").read()
        bad += s.count("](././images/") + s.count("](images/")
print("残留异常：%d 处" % bad)
