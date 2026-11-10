# -*- coding: utf-8 -*-
"""对比 _ynote_export 与 raw/文档 的文字一致性"""
import os, re, io, difflib

NEW = r"D:/workspace/ai_kb_base/_ynote_export"
OLD = r"D:/workspace/ai_kb_base/second-brain/raw/文档"

def norm(s):
    s = re.sub(r"^---\n.*?\n---\n", "", s, count=1, flags=re.S)      # front-matter
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)                         # 图片
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)                     # 链接保留锚文本
    s = re.sub(r"https?://\S+", "", s)                                  # 裸 URL
    s = re.sub(r"[#*`>|~\-\s]", "", s)                                  # 语法与空白
    return s

rows = []
for root, _, files in os.walk(NEW):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        np_ = os.path.join(root, fn)
        rel = os.path.relpath(np_, NEW).replace("\\", "/")
        op = os.path.join(OLD, rel)
        if not os.path.exists(op):
            rows.append((rel, None, None, "OLD缺失"))
            continue
        n = norm(io.open(np_, encoding="utf-8").read())
        o = norm(io.open(op, encoding="utf-8").read())
        if not o:
            rows.append((rel, len(n), 0, "OLD为空"))
            continue
        r = difflib.SequenceMatcher(None, o, n, autojunk=False).ratio()
        st = "OK" if r >= 0.98 else ("轻度" if r >= 0.9 else "偏差")
        rows.append((rel, len(o), len(n), "%.4f %s" % (r, st)))

bad = [x for x in rows if x[1] is None or not str(x[3]).startswith("1") ]
print("总计 %d 篇" % len(rows))
print("-" * 80)
low = sorted([x for x in rows if x[1] is not None and "OK" not in str(x[3])], key=lambda x: float(str(x[3]).split()[0]))
for rel, a, b, info in low:
    print("%-58s OLD=%-6s NEW=%-6s %s" % (rel[:58], a, b, info))
print("-" * 80)
print("需要关注：%d 篇" % len(low))
