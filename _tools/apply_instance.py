# -*- coding: utf-8 -*-
"""P2 补实例关系：概念 ──实例──> 实体，实体 ──实例化──> 概念。"""
import io
import os

CD = r"D:/workspace/ai_kb_base/second-brain/wiki/概念"

# 文件 → (锚点旧行, 新行含实例关系)
ADD = [
    ("数据湖.md",
     "- 相关：[[数据仓库]] · [[湖仓一体]] · [[数据中台]]",
     "- 实例：[[Iceberg]] —— 开源表格式实现，提供 ACID 与时间旅行\n"
     "- 相关：[[数据仓库]] · [[湖仓一体]] · [[数据中台]] · Hudi（未建页）"),
    ("湖仓一体.md",
     "- 相关：[[数据湖]] · [[数据仓库]] · [[数仓分层]]",
     "- 实例：[[Iceberg]] —— 用表格式把数据湖接上事务与 schema 演进\n"
     "- 相关：[[数据湖]] · [[数据仓库]] · [[数仓分层]] · Hudi（未建页）"),
    ("Iceberg.md",
     "- 相关：[[数据湖]] · [[湖仓一体]] · [[Spark]]",
     "- 实例化：[[数据湖]] · [[湖仓一体]] —— 同时实现这两个范式的诉求\n"
     "- 相关：[[Spark]]"),
    # HDFS 的组成补机架感知，与「机架感知 部分于 HDFS」对称
    ("HDFS.md",
     "- 组成：[[HDFS读写流程]] —— 读写流程是 HDFS 的核心机制",
     "- 组成：[[HDFS读写流程]] · [[机架感知]] —— 读写流程是核心机制，机架感知决定副本放置"),
]

for fn, old, new in ADD:
    p = os.path.join(CD, fn)
    s = io.open(p, encoding="utf-8").read()
    if old not in s:
        print("MISS %-10s %s" % (fn, old[:30]))
        continue
    io.open(p, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("OK   %-10s %s" % (fn, new.split("\n")[0][:40]))
