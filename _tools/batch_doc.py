# -*- coding: utf-8 -*-
"""
按 JSON 描述批量生成文档页。
用法：python batch_doc.py <json文件>
JSON 为数组，每项字段：
  file, title, source_path, modality, confidence, summary, note, concepts,
  claims: [{stmt, conf, ev}]
"""
import sys, os, io, json

D = r"D:/workspace/ai_kb_base/second-brain/wiki/文档"

def build(o):
    conf = o.get("confidence", 0.95)
    head = [
        "---",
        "type: doc",
        "title: %s" % o["title"],
        "source_path: %s" % o["source_path"],
        "source_type: youdao",
        "modality: %s" % o.get("modality", "text"),
        "confidence: %s" % conf,
        "compile_status: compiled",
        "compiled_at: 2026-11-06",
        "---",
        "",
        "# %s" % o["title"],
        "",
        "## 摘要",
        "",
        o.get("summary", "").strip(),
        "",
        "## 关键断言",
        "",
    ]
    body = []
    for c in o.get("claims", []):
        body.append("- %s  `%s`" % (c["stmt"], c["conf"]))
        body.append("  > 原文：「%s」" % c["ev"])
        body.append("")
    note = o.get("note", "").strip()
    tail = []
    if note:
        tail += ["> " + note, ""]
    tail += [
        "## 涉及概念",
        "",
        o.get("concepts", "（无独立概念页）").strip(),
        "",
        "## 原文位置",
        "",
        "`%s`" % o["source_path"],
        "",
    ]
    return "\n".join(head + body + tail)

jf = sys.argv[1]
data = json.load(io.open(jf, encoding="utf-8"))
n = 0
for o in data:
    p = os.path.join(D, o["file"])
    io.open(p, "w", encoding="utf-8", newline="").write(build(o))
    n += 1
    print("[OK] %s" % o["file"])
print("\n生成 %d 篇" % n)
