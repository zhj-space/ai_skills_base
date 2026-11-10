# -*- coding: utf-8 -*-
"""提取各章前言（副标题 + 本章定位）与「全书主线」「学习路线建议」两章完整内容"""
import io, re, json

SRC = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/数学/同济版高数知识点梳理.md"
lines = io.open(SRC, encoding="utf-8").read().split("\n")

# 章起点
chap_idx = [(i, ln[3:].strip()) for i, ln in enumerate(lines) if ln.startswith("## ")]

def compact_render(body):
    out, prev = [], None
    for x in body:
        t = x.strip()
        if not t:
            continue
        compact = t.startswith("-") or t.startswith("|")
        if prev and not compact:
            out.append("")
        out.append(t)
        if not compact:
            out.append("")
        prev = compact
    return "\n".join(out).strip()

preamble = {}
whole = {}
for k, (i, name) in enumerate(chap_idx):
    end = chap_idx[k+1][0] if k+1 < len(chap_idx) else len(lines)
    body = lines[i+1:end]
    if name in ("全书主线：三个问题，一条链", "学习路线建议"):
        whole[name] = compact_render(body)
        continue
    # 普通章：取到第一个条目号之前
    pre = []
    for x in body:
        if re.match(r"^\d+\.\d+[^\s]", x.strip()):
            break
        pre.append(x)
    preamble[name] = compact_render(pre)

out = {"preamble": preamble, "whole": whole}
io.open(r"D:/workspace/ai_kb_base/_tools/gaoshu_preamble.json", "w", encoding="utf-8", newline="") \
    .write(json.dumps(out, ensure_ascii=False, indent=1))

print("章前言：%d 章" % len(preamble))
for k, v in preamble.items():
    print("  %-14s %d 字" % (k, len(v)))
print("整章保留：%s" % list(whole.keys()))
for k, v in whole.items():
    print("  %s：%d 字" % (k, len(v)))
