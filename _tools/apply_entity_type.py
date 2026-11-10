# -*- coding: utf-8 -*-
"""P1 类型校形：按 ontology.json v2 重标 13 页 entity_type。
用法：python apply_entity_type.py --dry | --apply
只改 frontmatter 一行，不动七段正文。
"""
import io
import os
import re
import sys

CD = r"D:/workspace/ai_kb_base/second-brain/wiki/概念"
APPLY = "--apply" in sys.argv

ENTITIES = ["HDFS", "Spark", "Hive", "Kafka", "MapReduce", "YARN",
            "Sqoop", "Iceberg", "pgsql", "SQLServer", "JVM"]
METHODS = ["数据建模四步", "微元法"]

PLAN = {}
for x in ENTITIES:
    PLAN[x] = "实体"
for x in METHODS:
    PLAN[x] = "方法"

n = 0
print("=== P1 类型重标 ===")
for name, target in PLAN.items():
    p = os.path.join(CD, name + ".md")
    if not os.path.exists(p):
        print("  !! 缺文件 %s" % name)
        continue
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^entity_type:[ \t]*(\S+)$", s, re.M)
    if not m:
        print("  !! 无 entity_type %s" % name)
        continue
    cur = m.group(1)
    if cur == target:
        print("  -- %-16s 已是 %s" % (name, target))
        continue
    print("  OK %-16s %s -> %s" % (name, cur, target))
    if APPLY:
        s2 = s[:m.start()] + "entity_type: " + target + s[m.end():]
        io.open(p, "w", encoding="utf-8", newline="").write(s2)
    n += 1

print("\n%s %d 页" % ("已改" if APPLY else "待改", n))
