# -*- coding: utf-8 -*-
"""编译极短文本笔记：有文字但 <60 字，且无图片。建页并保留原文摘录。"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)
RE_WC = re.compile(r"^word_count:\s*(\d+)", re.M)
RE_IMG = re.compile(r"^images:\s*(\d+)", re.M)
RE_TITLE = re.compile(r"^title:\s*(.+)$", re.M)
RE_MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

covered, stems = set(), set()
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    stems.add(fn[:-3])
    s = io.open(os.path.join(DOC, fn), encoding="utf-8").read()
    m = RE_SP.search(s)
    if m:
        covered.add(m.group(1).strip().strip('"'))

targets = []
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, KB).replace(os.sep, "/")
        if rel in covered:
            continue
        s = io.open(p, encoding="utf-8").read()
        mw, mi = RE_WC.search(s), RE_IMG.search(s)
        w = int(mw.group(1)) if mw else -1
        n = int(mi.group(1)) if mi else 0
        if 0 < w < 60 and n == 0:
            targets.append((rel, s, w))

print("待生成短文本笔记页：%d 篇" % len(targets))

made = 0
for rel, s, w in targets:
    mt = RE_TITLE.search(s)
    title = mt.group(1).strip().strip('"') if mt else os.path.basename(rel)[:-3]
    body = s.split("---", 2)[-1]
    body = re.sub(r"^#.*$", "", body, flags=re.M).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)

    stem = "2026-11-06-%s" % re.sub(r'[\\/:*?"<>|]', "_", title)
    if stem in stems:
        tag = rel.replace("raw/docs/personal-assets/", "").rsplit("/", 1)[0].replace("/", "-")
        stem = "2026-11-06-%s-%s" % (re.sub(r'[\\/:*?"<>|]', "_", title), tag)
    k, base = 2, stem
    while stem in stems:
        stem = "%s_%d" % (base, k)
        k += 1
    stems.add(stem)

    L = []
    L.append("---")
    L.append("type: doc")
    L.append("title: %s" % title)
    L.append("source_path: %s" % rel)
    L.append("source_type: youdao")
    L.append("modality: text")
    L.append("confidence: 0.8")
    L.append("compile_status: compiled")
    L.append("compiled_at: 2026-11-06")
    L.append("---")
    L.append("")
    L.append("# %s" % title)
    L.append("")
    L.append("## 摘要")
    L.append("")
    L.append("极短笔记，原文仅 %d 字且无配图。内容不足以压缩成摘要，故原样留存于下方「原文摘录」，"
             "供日后回查。" % w)
    L.append("")
    L.append("## 关键断言")
    L.append("")
    L.append("（原文过短，未达「主语明确的完整句子」标准，不做断言抽取。`confidence: 0.8` 表示原文可信但不成体系。）")
    L.append("")
    L.append("## 原文摘录")
    L.append("")
    L.append("```")
    L.append(body if body else "（空）")
    L.append("```")
    L.append("")
    L.append("## 涉及概念")
    L.append("")
    L.append("（未挂接：原文无足够信息判断所属概念）")
    L.append("")
    L.append("## 原文位置")
    L.append("")
    L.append("`%s`" % rel)
    L.append("")

    io.open(os.path.join(DOC, stem + ".md"), "w", encoding="utf-8", newline="").write("\n".join(L))
    made += 1

print("已生成 %d 篇" % made)
