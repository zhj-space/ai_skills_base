# -*- coding: utf-8 -*-
"""提取原文全部知识点条目：编号 + 名称 + 标签 + 五段结构"""
import io, re, os, json

SRC = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/数学/同济版高数知识点梳理.md"
s = io.open(SRC, encoding="utf-8").read()
lines = s.split("\n")

# 找形如 "1.1数列极限（ε-N 定义）语言基石" 的行
pat = re.compile(r"^(\d+\.\d+)\s*(.+?)\s*([\u4e00-\u9fa5]{2,6})?$")

items = []
cur_ch = ""
for i, ln in enumerate(lines):
    if ln.startswith("## "):
        cur_ch = ln[3:].strip()
        continue
    t = ln.strip()
    if not t or t.startswith("#") or t.startswith("-") or t.startswith("*"):
        continue
    m = re.match(r"^(\d+\.\d+)([^\s].{1,40})$", t)
    if m:
        items.append({"ch": cur_ch, "no": m.group(1), "raw": m.group(2).strip(), "line": i+1})

print("共提取 %d 个知识点条目\n" % len(items))
cur = ""
for it in items:
    if it["ch"] != cur:
        print("## %s" % it["ch"]); cur = it["ch"]
    print("  %-6s %s" % (it["no"], it["raw"]))
