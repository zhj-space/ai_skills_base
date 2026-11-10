# -*- coding: utf-8 -*-
"""收尾 2：剩余中文目录改名 + 按 basename 重建 source_path（幂等）。"""
import io
import os
import re
import collections

KB = r"D:/workspace/ai_kb_base/second-brain"
P = "raw/docs/personal-assets/"

RENAME = [
    ("bigdata/etl相关", "bigdata/etl"),
    ("bigdata/hadoop运维", "bigdata/hadoop-ops"),
    ("bigdata/大数据资料", "bigdata/materials"),
    ("bigdata/数据架构/数据建模", "bigdata/data-architecture/modeling"),
    ("bigdata/数据架构/湖仓相关", "bigdata/data-architecture/lakehouse"),
    ("bigdata/数据架构", "bigdata/data-architecture"),
    ("bigdata/数据治理", "bigdata/governance"),
    ("java/java基础", "java/basics"),
    ("java/服务器", "java/server"),
    ("math/matlab编程", "math/matlab"),
    ("python/入门", "python/getting-started"),
    ("python/爬虫", "python/crawler"),
]

for old, new in RENAME:
    a, b = os.path.join(KB, P + old), os.path.join(KB, P + new)
    if os.path.isdir(a):
        if os.path.isdir(b):
            print("SKIP 目标已存在 %s" % new)
        else:
            os.makedirs(os.path.dirname(b), exist_ok=True)
            os.rename(a, b)
            print("DIR  %-40s -> %s" % (old, new))

# 残留中文目录检查
CN = re.compile(r"[\u4e00-\u9fa5]")
left = []
for r, ds, fs in os.walk(KB):
    if ".obsidian" in r:
        continue
    for d in ds:
        if CN.search(d):
            left.append(os.path.join(r, d).replace(KB, "").replace("\\", "/").lstrip("/"))
print("\n残留中文目录 %d 个 %s" % (len(left), left[:5]))

by_name = collections.defaultdict(list)
for r, _, fs in os.walk(os.path.join(KB, "raw")):
    for f in fs:
        if f.endswith(".md"):
            rel = os.path.relpath(os.path.join(r, f), KB).replace(os.sep, "/")
            by_name[f].append(rel)

DD = os.path.join(KB, "wiki", "summaries")
fixed = uniq = bad = 0
for f in sorted(os.listdir(DD)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(DD, f)
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    if not m:
        bad += 1
        continue
    cur = m.group(1).strip().strip('"').replace("\\", "/")
    if os.path.exists(os.path.join(KB, cur)):
        continue
    cand = by_name.get(os.path.basename(cur), [])
    if len(cand) == 1:
        s = s[:m.start(1)] + cand[0] + s[m.end(1):]
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        fixed += 1
    else:
        uniq += 1
        if uniq <= 5:
            print("  无法唯一匹配:", os.path.basename(cur), "->", len(cand), "个候选")

print("source_path 修复 %d 篇；无法唯一匹配 %d 篇；无字段 %d 篇" % (fixed, uniq, bad))
