# -*- coding: utf-8 -*-
"""按第八节契约校验证据并生成文档页"""
import os, io, re, json, sys

KB = r"D:/workspace/ai_kb_base/second-brain"
CT = r"D:/workspace/ai_kb_base/_tools/gaoshu_contract.json"
DOC = os.path.join(KB, "wiki", "summaries")

c = json.load(io.open(CT, encoding="utf-8"))
src = os.path.join(KB, c["src"])
raw = io.open(src, encoding="utf-8").read()
flat = re.sub(r"\s+", "", raw)

# ---- 步 4：校验 ----
fail = []
for i, cl in enumerate(c["claims"], 1):
    if cl["conf"] != "high":
        continue
    ev = re.sub(r"\s+", "", cl["evidence"])
    if ev not in flat:
        fail.append((i, cl["stmt"][:40], cl["evidence"][:70]))

print("断言 %d 条，high 校验：" % len(c["claims"]))
if fail:
    print("不匹配 %d 条 —— 回第 3 步重抽：" % len(fail))
    for i, s, e in fail:
        print("  #%d %s\n     证据: %s" % (i, s, e))
    sys.exit(1)
print("全部通过\n")

# ---- 步 5：写文档页 ----
stem = "2026-11-06-%s" % c["title"]
out = os.path.join(DOC, stem + ".md")

L = []
L.append("---")
L.append("type: doc")
L.append("doc_id: gaoshu-tongji-20261106")
L.append("title: %s" % c["title"])
L.append("source_path: %s" % c["src"])
L.append("source_type: %s" % c["source_type"])
L.append("modality: %s" % c["modality"])
L.append("confidence: %s" % c["confidence"])
L.append("compile_status: compiled")
L.append("compiled_at: 2026-11-06")
L.append("---")
L.append("")
L.append("# %s" % c["title"])
L.append("")
L.append("## 摘要")
L.append("")
L.append(c["summary"])
L.append("")
L.append("## 关键断言")
L.append("")
for cl in c["claims"]:
    if cl["conf"] == "high":
        L.append("- %s  `high`" % cl["stmt"])
        L.append("  > 原文：「%s」" % cl["evidence"])
    else:
        L.append("- %s  `%s`" % (cl["stmt"], cl["conf"]))
        L.append("  > %s" % cl["evidence"])
    L.append("")
L.append("> 注：本篇正文 3.9 万字，含 12 章 60 个概念的完整讲解；本页按「压到原文 10–20%」的要求抽取跨章核心判断与关键定义，细部推导与公式见原文。原文含 LaTeX 式纯文本公式，转换时保留原字符未改。")
L.append("")
L.append("## 涉及概念")
L.append("")
L.append(" · ".join("[[%s]]" % x for x in c["concepts"]))
L.append("")
L.append("## 原文位置")
L.append("")
L.append("`%s`" % c["src"])
L.append("")
L.append("> 原件：`raw/docs/personal-assets/数学/同济版高数知识点梳理.html`（173K，HTML 排版源）")
L.append("")

io.open(out, "w", encoding="utf-8", newline="").write("\n".join(L))
chars = sum(len(x) for x in L)
ratio = chars / len(re.sub(r"\s+", "", re.sub(r"^---.*?---", "", raw, flags=re.S)))
print("已写文档页：%s" % out)
print("压缩比：%.1f%%（原文 30005 有效字符 → 文档页 %d 字符）" % (ratio * 100, chars))
