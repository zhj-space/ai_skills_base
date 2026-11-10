# -*- coding: utf-8 -*-
"""把新工作区里脚本与 skill 的硬编码路径从旧库改到新库"""
import os, io

NEW = r"D:/workspace/ai_kb_base"
OLDF = "D:/workspace/ai_kb_base"
OLDB = "D:\\知识库"
NEWB = NEW.replace("/", "\\")

targets = []
for root, _, fs in os.walk(NEW):
    for fn in fs:
        if fn.endswith((".py", ".md")):
            targets.append(os.path.join(root, fn))

changed = 0
for p in targets:
    try:
        s = io.open(p, encoding="utf-8").read()
    except Exception:
        continue
    o = s
    s = s.replace(OLDB, NEWB).replace(OLDF, NEW)
    if s != o:
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        changed += 1

print("扫描 %d 个文件，改写 %d 个" % (len(targets), changed))

left = []
for p in targets:
    try:
        s = io.open(p, encoding="utf-8").read()
    except Exception:
        continue
    if OLDF in s or OLDB in s:
        left.append(os.path.relpath(p, NEW))
print("仍含旧路径：%d" % len(left))
for x in left[:10]:
    print("   ", x)
