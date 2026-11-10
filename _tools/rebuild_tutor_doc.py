# -*- coding: utf-8 -*-
"""重编译教程文档页的「原文全文 · 逐字保留」段。

规则：raw 正文整段搬进来，标题统一加两个 #（# → ###，## → ####），
但代码块内的行首 # 不动（否则 ```bash 里的 "# 体检" 会被当成标题）。

重建方式：从「## 原文全文 · 逐字保留」这一行起整段重写，
不依赖后面的具体标题长什么样，可反复重跑而不叠加层级。
"""
import re
from pathlib import Path

ROOT = Path(r"D:/workspace/ai_kb_base")
RAW = ROOT / "second-brain/raw/docs/personal-assets/ops/知识库搭建与运维教程.md"
DOC = ROOT / "second-brain/wiki/summaries/2026-11-09-个人知识库搭建与运维教程.md"

MARKER = "## 原文全文 · 逐字保留"
NOTE = "> 原文逐字保留，标题统一降级以并入本段。章级提炼见 [[编译式知识库]] 与 [[知识库搭建六阶段]]。"

raw = RAW.read_bytes().decode("utf-8")
body = re.sub(r"^---\n.*?\n---\n\n", "", raw, flags=re.S)

out = []
in_code = False
demoted = 0
for line in body.split("\n"):
    if line.startswith("```") or line.startswith("~~~"):
        in_code = not in_code
        out.append(line)
        continue
    if not in_code and re.match(r"^#{1,4} ", line):
        line = "##" + line
        demoted += 1
    out.append(line)
render = "\n".join(out)

doc = DOC.read_bytes().decode("utf-8")
if MARKER not in doc:
    raise SystemExit("找不到段落标记，中止（不动文件）")

head = doc[: doc.index(MARKER)]
new = head + MARKER + "\n\n" + NOTE + "\n\n" + render
DOC.write_bytes(new.encode("utf-8"))

print(f"降级标题 {demoted} 个（每个 +2 级）")
print(f"文档页 {len(doc.splitlines())} → {len(new.splitlines())} 行")
print(f"CRLF 数: {new.count(chr(13) + chr(10))}")
