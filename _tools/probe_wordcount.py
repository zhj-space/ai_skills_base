# -*- coding: utf-8 -*-
"""反推 word_count 的计数口径。

用途：库里 322 篇 raw 带 word_count 字段，17 个脚本在读它，
但口径没有文档。此脚本用多个文件对比几种常见算法，找出能对上的那个。
"""
import re
from pathlib import Path

KB = Path(r"D:/workspace/ai_kb_base/second-brain/raw")
FM = re.compile(r"^---\n.*?\n---\n", re.S)
DECL = re.compile(r"^word_count:\s*(\d+)", re.M)
PAT_CJK = re.compile(r"[\u4e00-\u9fa5]")
PAT_EN = re.compile(r"[A-Za-z]+")
PAT_DIG = re.compile(r"\d+")


def measure(body):
    cjk = len(PAT_CJK.findall(body))
    en = len(PAT_EN.findall(body))
    dig = len(PAT_DIG.findall(body))
    nos = len(re.sub(r"\s", "", body))
    return cjk, en, dig, nos, len(body)


rows = []
for p in sorted(KB.rglob("*.md")):
    t = p.read_bytes().decode("utf-8", "replace")
    m = DECL.search(t)
    if not m:
        continue
    body = FM.sub("", t)
    rows.append((int(m.group(1)),) + measure(body) + (p.name,))
    if len(rows) >= 10:
        break

if not rows:
    print("没有找到带 word_count 的文件")
    raise SystemExit(1)

print(f"共取样 {len(rows)} 篇\n")
print(f"{'声明':>7} {'中文':>6} {'英词':>5} {'数串':>5} {'去空白':>7} {'总字符':>7}  文件")
for d, c, e, g, n, tot, name in rows:
    print(f"{d:>7} {c:>6} {e:>5} {g:>5} {n:>7} {tot:>7}  {name[:26]}")

print("\n差值检验（声明 − 各候选）：")
print(f"{'声明−中文':>9} {'−英词':>7} {'−数串':>7} {'−去空白':>8}  文件")
for d, c, e, g, n, tot, name in rows:
    print(f"{d-c:>9} {d-e:>7} {d-g:>7} {d-n:>8}  {name[:26]}")

print("\n候选口径平均绝对误差：")
cands = {
    "中文字数": [abs(d - c) for d, c, e, g, n, tot, _ in rows],
    "英文单词数": [abs(d - e) for d, c, e, g, n, tot, _ in rows],
    "中文+英词": [abs(d - (c + e)) for d, c, e, g, n, tot, _ in rows],
    "中文+英词+数串": [abs(d - (c + e + g)) for d, c, e, g, n, tot, _ in rows],
    "去空白字符数": [abs(d - n) for d, c, e, g, n, tot, _ in rows],
}
for k, v in cands.items():
    print(f"  {k:<14} {sum(v)/len(v):>8.1f}")
