# -*- coding: utf-8 -*-
"""只检测实质缺失：旧版有、新版没有的连续文字片段（>=8字）"""
import os, re, io, difflib

NEW = r"D:/workspace/ai_kb_base/_ynote_export"
OLD = r"D:/workspace/ai_kb_base/second-brain/raw/文档"

def norm(s):
    s = re.sub(r"^---\n.*?\n---\n", "", s, count=1, flags=re.S)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"https?://\S+", "", s)
    s = re.sub(r"^\s*#\s+.*$", "", s, count=1, flags=re.M)   # 去掉一级标题（换库时会补）
    s = re.sub(r"[#*`>|]", "", s)
    s = re.sub(r"\s+", "", s)
    return s

miss = []
for root, _, files in os.walk(NEW):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        np_ = os.path.join(root, fn)
        rel = os.path.relpath(np_, NEW).replace("\\", "/")
        op = os.path.join(OLD, rel)
        if not os.path.exists(op):
            continue
        o = norm(io.open(op, encoding="utf-8").read())
        n = norm(io.open(np_, encoding="utf-8").read())
        if not o or not n:
            continue
        segs = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, o, n, autojunk=False).get_opcodes():
            if tag in ("delete", "replace") and (i2 - i1) >= 8:
                segs.append(o[i1:i2])
        if segs:
            miss.append((rel, sum(len(x) for x in segs), segs))

miss.sort(key=lambda x: -x[1])
print("存在实质缺失的篇数：%d" % len(miss))
print("=" * 90)
for rel, ln, segs in miss[:25]:
    print("%s  [缺 %d 字]" % (rel, ln))
    for s in segs[:4]:
        print("     >>> %s" % s[:120])
print("=" * 90)
print("合计缺失字数：%d" % sum(x[1] for x in miss))
