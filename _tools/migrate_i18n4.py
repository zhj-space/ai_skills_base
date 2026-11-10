# -*- coding: utf-8 -*-
"""收尾 3：合并残留目录 + 用旧路径提示消解 5 篇歧义。"""
import io
import os
import re
import shutil

KB = r"D:/workspace/ai_kb_base/second-brain"
P = "raw/docs/personal-assets/"

# 1) 合并 bigdata/数据架构 -> bigdata/data-architecture
src = os.path.join(KB, P + "bigdata/数据架构")
dst = os.path.join(KB, P + "bigdata/data-architecture")
if os.path.isdir(src):
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(src):
        a, b = os.path.join(src, name), os.path.join(dst, name)
        if os.path.exists(b):
            print("冲突 %s" % name)
            continue
        shutil.move(a, b)
        print("MOVE %s -> data-architecture/" % name)
    try:
        os.rmdir(src)
        print("已删除 bigdata/数据架构")
    except OSError as e:
        print("未删净", e)

# 2) 5 篇歧义页显式指向
FIX = {
    "2026-11-06-linux命令.md": P + "os/linux/linux命令.md",
    "2026-11-06-linux常用命令.md": P + "ops/linux命令.md",
    "2026-11-06-个人总结-数据架构.md": P + "bigdata/data-architecture/个人总结.md",
    "2026-11-06-应用系统间数据传递方式.md": P + "architecture/应用系统之间数据传递的几种方式.md",
    "2026-11-06-数据建模选择与对比.md": P + "bigdata/data-architecture/modeling/个人总结.md",
}

DD = os.path.join(KB, "wiki", "summaries")
for fn, target in FIX.items():
    p = os.path.join(DD, fn)
    if not os.path.exists(p):
        print("MISS %s" % fn)
        continue
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    if not m:
        print("MISS 无字段 %s" % fn)
        continue
    ok = os.path.exists(os.path.join(KB, target))
    s = s[:m.start(1)] + target + s[m.end(1):]
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("%s %-40s -> %s" % ("OK " if ok else "BAD", fn[:38], target.split("personal-assets/")[-1]))
