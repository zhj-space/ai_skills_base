# -*- coding: utf-8 -*-
"""判定点 A：新入库这篇与库内已有笔记的重叠度（字符 3-gram）"""
import os, io, re

KB = r"D:/workspace/ai_kb_base/second-brain"
NEW = os.path.join(KB, "raw", "summaries", "个人资产体系", "数学", "同济版高数知识点梳理.md")
DIR = os.path.join(KB, "raw", "summaries", "个人资产体系", "数学")


def norm(s):
    s = re.sub(r"^---.*?---", "", s, flags=re.S)
    return re.sub(r"[\s，。、；：（）()【】「」《》·—\-=+*/\\|_`*#>~\[\]{}:;,.!?\"']", "", s)


def grams(s, n=3):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


new = norm(io.open(NEW, encoding="utf-8").read())
gn = grams(new)
print("新篇有效字符：%d，3-gram：%d\n" % (len(new), len(gn)))

rows = []
for fn in sorted(os.listdir(DIR)):
    p = os.path.join(DIR, fn)
    if not fn.endswith(".md") or p == NEW:
        continue
    s = norm(io.open(p, encoding="utf-8").read())
    if len(s) < 50:
        continue
    g = grams(s)
    if not g:
        continue
    inter = len(gn & g)
    cov = inter / len(g)          # 旧篇被新篇覆盖的比例
    rows.append((cov, len(s), fn))

rows.sort(reverse=True)
print("%-34s %8s %10s" % ("库内已有笔记", "字数", "覆盖率"))
print("-" * 56)
for cov, ln, fn in rows[:15]:
    flag = "← 高度重叠" if cov >= 0.6 else ""
    print("%-34s %8d %9.1f%% %s" % (fn[:-3], ln, cov * 100, flag))
