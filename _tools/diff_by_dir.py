# -*- coding: utf-8 -*-
"""精确对比：分目录统计，排除备份"""
import os, io, hashlib, collections

OLD = r"D:/知识库"
NEW = r"D:/workspace/ai_kb_base"

def snap(base, sub=""):
    root0 = os.path.join(base, sub) if sub else base
    out = {}
    for root, _, fs in os.walk(root0):
        for fn in fs:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, root0).replace(os.sep, "/")
            try:
                out[rel] = os.path.getsize(p)
            except OSError:
                pass
    return out

# 分目录比
for sub in ["second-brain", "_tools", "llm-wiki-skills", "_ynote_export"]:
    o = snap(OLD, sub)
    n = snap(NEW, sub)
    miss = sorted(set(o) - set(n))
    extra = sorted(set(n) - set(o))
    print("### %s" % sub)
    print("   旧 %d / 新 %d   缺失 %d / 新增 %d" % (len(o), len(n), len(miss), len(extra)))
    for x in miss[:8]:
        print("      [缺] %s" % x)
    for x in extra[:8]:
        print("      [多] %s" % x)
    print()

# 根目录散文件
def rootsnap(base):
    out = {}
    for fn in os.listdir(base):
        p = os.path.join(base, fn)
        if os.path.isfile(p):
            out[fn] = os.path.getsize(p)
    return out

o, n = rootsnap(OLD), rootsnap(NEW)
print("### 根目录散文件")
print("   旧 %s" % sorted(o.keys()))
print("   新 %s" % sorted(n.keys()))
print()

# 旧根目录的备份目录
print("### 旧根目录的子目录")
for d in sorted(os.listdir(OLD)):
    p = os.path.join(OLD, d)
    if os.path.isdir(p):
        cnt = sum(1 for _, _, fs in os.walk(p) for _ in fs)
        print("   %-40s %d 个文件" % (d, cnt))
