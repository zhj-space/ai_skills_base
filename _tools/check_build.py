# -*- coding: utf-8 -*-
"""校验构建产物：篇数、图片引用、front-matter 完整性"""
import os, re, io
from urllib.parse import unquote

BUILD = r"D:/workspace/ai_kb_base/_build_sources_文档/个人资产体系"

mds, imgs = [], []
for root, dirs, files in os.walk(BUILD):
    for fn in files:
        p = os.path.join(root, fn)
        if fn.endswith(".md"):
            mds.append(p)
        elif os.path.basename(root) == "images":
            imgs.append(p)

print("md 篇数：%d" % len(mds))
print("图片张数：%d" % len(imgs))

missing, total_ref = [], 0
bad_fm, no_h1 = [], []
for p in mds:
    s = io.open(p, encoding="utf-8").read()
    d = os.path.dirname(p)
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", s):
        url = m.group(1).strip()
        if url.startswith("http"):
            missing.append((p, url, "远程"))
            continue
        total_ref += 1
        if not os.path.exists(os.path.join(d, url)) and not os.path.exists(os.path.join(d, unquote(url))):
            missing.append((p, url, "本地缺失"))
    if not s.startswith("---\n"):
        bad_fm.append(p)
    elif "\n# " not in s[:600]:
        no_h1.append(p)

print("图片引用总数：%d" % total_ref)
print("引用异常：%d" % len(missing))
for p, u, why in missing[:15]:
    print("   [%s] %s  <- %s" % (why, u[:80], os.path.relpath(p, BUILD)))
print("front-matter 异常：%d" % len(bad_fm))
print("缺 H1 标题：%d" % len(no_h1))
for p in no_h1[:5]:
    print("   " + os.path.relpath(p, BUILD))

print("\n=== 抽样 3 篇 front-matter ===")
for p in mds[:2] + [mds[len(mds)//2]]:
    s = io.open(p, encoding="utf-8").read()
    print("-" * 60)
    print(os.path.relpath(p, BUILD))
    print("\n".join(s.split("\n")[:14]))
