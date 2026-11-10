"""把 59 篇「无独立概念页」文档页挂到新建的概念/实体页上。

按原有豁免文案判定归属，不做模糊匹配：
  含「属 Worklight」 → [[Worklight]] · [[混合应用]]
  含「属 MATLAB」    → [[MATLAB]]
  含「属 Python」    → [[Python]]

用法：python apply_concept_links.py --dry | --apply
"""
import io
import os
import re
import sys

KB = r"D:/workspace/ai_kb_base/second-brain"
DOC = os.path.join(KB, "wiki", "summaries")
DRY = "--apply" not in sys.argv

RULES = [
    ("属 Worklight", "[[Worklight]] · [[混合应用]]"),
    ("属 MATLAB", "[[MATLAB]]"),
    ("属 Python", "[[Python]]"),
]

PAT = re.compile(r"(## 涉及概念\n\n)(（无独立概念页[^\n]*）)(\n\n## 原文位置)", re.S)

hit = miss = skip = 0
for f in sorted(os.listdir(DOC)):
    if not f.endswith(".md"):
        continue
    p = os.path.join(DOC, f)
    s = io.open(p, encoding="utf-8").read()
    m = PAT.search(s)
    if not m:
        continue
    old = m.group(2)
    new = None
    for key, link in RULES:
        if key in old:
            new = link
            break
    # 兜底：按源路径归属（豁免文案不统一时用）
    if not new:
        ms = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
        sp = (ms.group(1) if ms else "").lower()
        if "worklight" in sp:
            new = "[[Worklight]] · [[混合应用]]"
        elif "matlab" in sp:
            new = "[[MATLAB]]"
        elif "python" in sp:
            new = "[[Python]]"
    if not new:
        miss += 1
        print("  ?? 未匹配规则：%-40s %s" % (f[:-3][:38], old[:40]))
        continue
    s2 = s[:m.start(2)] + new + s[m.end(2):]
    if not DRY:
        io.open(p, "w", encoding="utf-8", newline="").write(s2)
    print("  OK %-42s %s" % (f[:-3][:40], new))
    hit += 1

print("\n%s：挂接 %d 篇，未匹配 %d 篇" % ("预演" if DRY else "已落盘", hit, miss))
