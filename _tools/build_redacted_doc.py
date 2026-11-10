# -*- coding: utf-8 -*-
"""把 raw 正文搬进文档页的「原文全文」段，同时遮蔽 UUID。

为什么单独写脚本而不直接复制：这篇原文里有一个 v2ray 服务端 UUID，
原文注明「也是密码」，等同访问凭据。文档页要上传到 GitHub，必须遮蔽；
但 raw 原文保持完整（本地不上传），所以两边不能简单复制。

标题统一降级 +2 级并入本页；代码块内的行首 # 不动。
"""
import re
from pathlib import Path

ROOT = Path(r"D:/workspace/ai_kb_base")
RAW = ROOT / "second-brain/raw/docs/personal-assets/creation/科学上网部署.md"
DOC = ROOT / "second-brain/wiki/summaries/2026-11-09-科学上网部署.md"

UUID = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
MASK = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

raw = RAW.read_bytes().decode("utf-8")
body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)

body, n_uuid = UUID.subn(MASK, body)

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
marker = "## 原文全文 · 逐字保留（UUID 已遮蔽）"
if marker not in doc:
    raise SystemExit("文档页缺少全文段标记，中止")
head = doc[: doc.index(marker)]
new = head + marker + "\n\n" + render.rstrip("\n") + "\n"

DOC.write_bytes(new.encode("utf-8"))
print(f"遮蔽 UUID {n_uuid} 处")
print(f"降级标题 {demoted} 个")
print(f"文档页 {len(doc.splitlines())} → {len(new.splitlines())} 行")
print(f"CRLF 数: {new.count(chr(13) + chr(10))}")
