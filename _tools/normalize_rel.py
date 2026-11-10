# -*- coding: utf-8 -*-
"""把旧关系词归一到 ontology.json 的正式词表。改前逐条核对，改后复验。"""
import io
import os

CD = r"D:/workspace/ai_kb_base/second-brain/wiki/概念"

FIX = [
    ("HDFS.md", "- 机制：[[HDFS读写流程]]",
     "- 组成：[[HDFS读写流程]] —— 读写流程是 HDFS 的核心机制"),
    ("HDFS读写流程.md", "- 约束：[[租约机制]] —— 写入前必须先拿到租约",
     "- 相关：[[租约机制]] —— 写入前必须先拿到租约，属硬约束"),
    ("思维体系模型.md", "- 下位应用：[[数据建模四步]]",
     "- 应用：[[数据建模四步]] —— 四步法是本模型在数据建模上的具体化"),
    ("思维体系模型.md", "- 输出：可复用的解题与建模流程",
     "- 产出：可复用的解题与建模流程"),
    ("极限.md", "- 前置保证：[[实数完备性]] —— 保证「逼近」一定落在某个实数上",
     "- 前置：[[实数完备性]] —— 保证「逼近」一定落在某个实数上"),
]

for fn, old, new in FIX:
    p = os.path.join(CD, fn)
    s = io.open(p, encoding="utf-8").read()
    if old not in s:
        print("!! 未匹配 %-16s %s" % (fn, old[:24]))
        continue
    io.open(p, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    print("OK  %-16s %s" % (fn, old[:14]))
