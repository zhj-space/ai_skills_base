# -*- coding: utf-8 -*-
"""批量打印指定 source 的正文（去掉 front-matter），用于集中阅读"""
import sys, os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
for rel in sys.argv[1:]:
    p = os.path.join(KB, rel)
    if not os.path.exists(p):
        p = os.path.join(KB, "raw", "summaries", "个人资产体系", rel)
    if not os.path.exists(p):
        print("### 未找到: %s" % rel)
        continue
    s = io.open(p, encoding="utf-8").read()
    s = re.sub(r"^---\n.*?\n---\n", "", s, count=1, flags=re.S)
    print("=" * 70)
    print("FILE: %s" % os.path.relpath(p, KB).replace(os.sep, "/"))
    print("=" * 70)
    print(s.strip())
    print()
