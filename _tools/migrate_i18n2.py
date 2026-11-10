# -*- coding: utf-8 -*-
"""收尾：把残留中文子目录改成英文，并按实际位置重建 source_path。"""
import io
import os
import re
import collections

KB = r"D:/workspace/ai_kb_base/second-brain"

RENAME = [
    ("raw/docs/personal-assets/android/Ibm Worklight/事件", "raw/docs/personal-assets/android/worklight/events"),
    ("raw/docs/personal-assets/android/Ibm Worklight/基础", "raw/docs/personal-assets/android/worklight/basics"),
    ("raw/docs/personal-assets/android/Ibm Worklight/小技巧", "raw/docs/personal-assets/android/worklight/tips"),
    ("raw/docs/personal-assets/android/Ibm Worklight/方法", "raw/docs/personal-assets/android/worklight/methods"),
    ("raw/docs/personal-assets/android/Ibm Worklight", "raw/docs/personal-assets/android/worklight"),
    ("raw/docs/personal-assets/bigdata/etl相关", "raw/docs/personal-assets/bigdata/etl"),
    ("raw/docs/personal-assets/bigdata/hadoop运维", "raw/docs/personal-assets/bigdata/hadoop-ops"),
    ("raw/docs/personal-assets/bigdata/大数据资料", "raw/docs/personal-assets/bigdata/materials"),
    ("raw/docs/personal-assets/bigdata/数据架构/数据建模", "raw/docs/personal-assets/bigdata/data-architecture/modeling"),
    ("raw/docs/personal-assets/bigdata/数据架构/湖仓相关", "raw/docs/personal-assets/bigdata/data-architecture/lakehouse"),
    ("raw/docs/personal-assets/bigdata/数据架构", "raw/docs/personal-assets/bigdata/data-architecture"),
    ("raw/docs/personal-assets/bigdata/数据治理", "raw/docs/personal-assets/bigdata/governance"),
    ("raw/docs/personal-assets/java/java基础", "raw/docs/personal-assets/java/basics"),
    ("raw/docs/personal-assets/java/服务器", "raw/docs/personal-assets/java/server"),
    ("raw/docs/personal-assets/math/matlab编程", "raw/docs/personal-assets/math/matlab"),
    ("raw/docs/personal-assets/python/入门", "raw/docs/personal-assets/python/getting-started"),
    ("raw/docs/personal-assets/python/爬虫", "raw/docs/personal-assets/python/crawler"),
]

for old, new in RENAME:
    a, b = os.path.join(KB, old), os.path.join(KB, new)
    if os.path.isdir(a):
        os.makedirs(os.path.dirname(b), exist_ok=True)
        os.rename(a, b)
        print("DIR %-58s -> %s" % (old.split("personal-assets/")[-1], new.split("personal-assets/")[-1]))

# 按 basename 建索引
by_name = collections.defaultdict(list)
for r, _, fs in os.walk(os.path.join(KB, "raw")):
    for f in fs:
        if f.endswith(".md"):
            rel = os.path.relpath(os.path.join(r, f), KB).replace(os.sep, "/")
            by_name[f].append(rel)

dups = {k: v for k, v in by_name.items() if len(v) > 1}
print("\n同名源文件 %d 组 %s" % (len(dups), list(dups)[:3]))

DD = os.path.join(KB, "wiki", "summaries")
fixed = unresolved = 0
for f in sorted(os.listdir(DD)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(DD, f)
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    if not m:
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
        unresolved += 1

print("重建 source_path：修复 %d 篇，无法唯一匹配 %d 篇" % (fixed, unresolved))
