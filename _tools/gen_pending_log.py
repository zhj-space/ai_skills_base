# -*- coding: utf-8 -*-
"""
生成待办日志（精简版）：只记数量总账 + 未完成构成 + 清单。
输出：D:/workspace/ai_kb_base/待办日志-2026-11-06.md
可重复运行刷新。
"""
import os, re, io, time

KB = r"D:/workspace/ai_kb_base/second-brain"
OUT = r"D:/workspace/ai_kb_base/待办日志-2026-11-06.md"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")
DIG = os.path.join(KB, "wiki", "analysis")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)
RE_WC = re.compile(r"^word_count:\s*(\d+)", re.M)
RE_IMG = re.compile(r"^images:\s*(\d+)", re.M)

# ---------- 覆盖情况 ----------
covered = set()
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = RE_SP.search(s)
    if m:
        sp = m.group(1).strip().strip('"')
        if os.path.exists(os.path.join(KB, sp)):
            covered.add(sp)

# ---------- 全量 source ----------
all_src = []
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if fn.endswith(".md"):
            all_src.append(os.path.relpath(os.path.join(root, fn), KB).replace(os.sep, "/"))

empty_notes, pure_img, sensitive = [], [], []
for rel in all_src:
    if rel in covered:
        continue
    s = io.open(os.path.join(KB, rel), encoding="utf-8").read()
    mw, mi = RE_WC.search(s), RE_IMG.search(s)
    w = int(mw.group(1)) if mw else -1
    n = int(mi.group(1)) if mi else 0
    short = rel.replace("raw/docs/personal-assets/", "")
    if w == 0 and n == 0:
        empty_notes.append(short)
    elif w < 60:
        pure_img.append(short)
    else:
        sensitive.append(short)

n_src = len(all_src)
n_write = n_src - len(empty_notes) - len(pure_img) - len(sensitive)
n_digest = len([f for f in os.listdir(DIG)
                if f.endswith(".md") and not f.startswith("沉淀索引")])
n_un = len(empty_notes) + len(pure_img) + len(sensitive)

L = []
A = L.append

A("# 待办日志 · 2026-11-06")
A("")
A("> 生成时间：%s　｜　刷新：`cd D:/workspace/ai_kb_base/_tools && python gen_pending_log.py`" % time.strftime("%Y-%m-%d %H:%M"))
A("")

A("## 数量总账")
A("")
A("| 项 | 数量 |")
A("|---|---|")
A("| 原始数量（sources 原文） | **%d** |" % n_src)
A("| 写入完成（编译为 wiki 文档页） | **%d** |" % n_write)
A("| 沉淀完成（wiki 问答沉淀页） | **%d** |" % n_digest)
A("| 未完成 | **%d** |" % n_un)
A("")
A("写入完成率：**%.1f%%**（%d / %d）" % (n_write * 100.0 / n_src, n_write, n_src))
A("")
n_withhold = len([f for f in os.listdir(DOC) if f.endswith(".md") and "凭据已屏蔽" in f])
A("> 口径：写入 %d = **%d 篇正常文档页 + %d 篇凭据屏蔽页**（后者含凭据，不进索引检索）；"
  % (n_write, n_write - n_withhold, n_withhold))
A("> 沉淀 %d 篇是问答产出，不来自 sources，故不计入上面的分母。" % n_digest)
A("")

A("## 未完成 %d 篇的构成" % n_un)
A("")
A("| 类型 | 数量 | 说明 |")
A("|---|---|---|")
A("| 真空笔记 | %d | 0 字 0 图，导出源即空 |" % len(empty_notes))
A("| 纯图片笔记 | %d | 有图、正文不足 60 字 |" % len(pure_img))
A("| 涉敏笔记 | %d | 主动跳过，仅保留原文 |" % len(sensitive))
A("")

if empty_notes:
    A("## 未完成清单 · 真空笔记（%d）" % len(empty_notes))
    A("")
    for x in sorted(empty_notes):
        A("- `%s`" % x)
    A("")

if pure_img:
    A("## 未完成清单 · 纯图片笔记（%d）" % len(pure_img))
    A("")
    for x in sorted(pure_img):
        A("- `%s`" % x)
    A("")

if sensitive:
    A("## 未完成清单 · 涉敏笔记（%d）" % len(sensitive))
    A("")
    for x in sorted(sensitive):
        A("- `%s`" % x)
    A("")

io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
print("原始 %d ｜ 写入 %d ｜ 沉淀 %d ｜ 未完成 %d（真空 %d / 纯图 %d / 涉敏 %d）"
      % (n_src, n_write, n_digest, n_un, len(empty_notes), len(pure_img), len(sensitive)))
print("已写入 %s（%d 行）" % (OUT, len(L)))
