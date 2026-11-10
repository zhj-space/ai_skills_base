# -*- coding: utf-8 -*-
"""按本体规范补数据：C9 结构关系 + C8 版本/缺口声明。
每条都写明原文依据；无依据的一律写「信息缺口」，不编造版本号。
"""
import io
import os
import re

CD = r"D:/workspace/ai_kb_base/second-brain/wiki/概念"

# ── C9：补结构关系（依据全部取自该页「是什么」原文） ──
C9 = [
    ("Hive.md",
     "- 相关：[[MapReduce]] · [[Spark]] · [[HDFS]] · [[Sqoop]]",
     "- 实例化：[[数据仓库]] —— Hive 是构建在 Hadoop 之上的数仓工具\n"
     "- 相关：[[MapReduce]] · [[Spark]] · [[HDFS]] · [[Sqoop]]"),
    ("SQLServer.md",
     "- 相关：[[SQL运维]] · [[pgsql]]",
     "- 实例化：[[数据库系统]] —— 微软的关系型数据库实现\n"
     "- 相关：[[SQL运维]] · [[pgsql]]"),
    ("pgsql.md",
     "- 相关：[[SQL运维]] · [[SQLServer]]",
     "- 实例化：[[数据库系统]] —— 开源关系型数据库实现\n"
     "- 相关：[[SQL运维]] · [[SQLServer]]"),
    ("MapReduce.md",
     "- 相关：[[YARN]] · [[HDFS]] · [[Spark]] · [[Hive]]",
     "- 实例化：[[移动计算]] —— 把计算推到数据所在节点\n"
     "- 相关：[[YARN]] · [[HDFS]] · [[Spark]] · [[Hive]]"),
    ("Sqoop.md",
     "- 相关：[[Hive]] · [[HDFS]] · [[MapReduce]]",
     "- 前置：[[MapReduce]] —— 本质是生成 MapReduce 作业来搬运数据\n"
     "- 相关：[[Hive]] · [[HDFS]] · [[MapReduce]]"),
]

# ── C8：库内无版本/选型资料的页，显式声明缺口（不编造） ──
C8 = ["HDFS", "Hive", "JVM", "Kafka", "SQLServer", "Spark", "pgsql"]
GAP = "- **信息缺口**：库内无版本与替代选型资料，本页不回答「该用哪个版本、什么时候该换掉」。"

ok = miss = 0
for fn, old, new in C9:
    p = os.path.join(CD, fn)
    s = io.open(p, encoding="utf-8").read()
    if old not in s:
        print("MISS-C9 %-14s %s" % (fn, old[:26]))
        miss += 1
        continue
    io.open(p, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("OK-C9   %-14s %s" % (fn, new.split("\n")[0][:44]))
    ok += 1

for name in C8:
    p = os.path.join(CD, name + ".md")
    s = io.open(p, encoding="utf-8").read()
    if "信息缺口" in s:
        print("SKIP-C8 %-14s 已有" % name)
        continue
    if "## 常见误区" not in s:
        print("MISS-C8 %-14s 无常见误区节" % name)
        miss += 1
        continue
    # 插到「常见误区」节最后一个列表项之后
    head, rest = s.split("## 常见误区", 1)
    tail = rest.split("\n## ", 1)
    body = tail[0].rstrip()
    after = "\n## " + tail[1] if len(tail) > 1 else ""
    s2 = head + "## 常见误区" + body + "\n" + GAP + "\n" + after
    io.open(p, "w", encoding="utf-8", newline="").write(s2)
    print("OK-C8   %-14s 已加缺口声明" % name)
    ok += 1

print("\n改 %d 处，未匹配 %d 处" % (ok, miss))
