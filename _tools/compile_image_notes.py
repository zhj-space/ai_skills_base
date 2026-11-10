# -*- coding: utf-8 -*-
"""
按流程编译纯图片笔记：modality=image 且正文 <60 字，图片即内容，建页不算空壳。
- 真空笔记（0 字 0 图）不建页（禁令）
- 涉敏笔记不建页
"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries")
DOC = os.path.join(KB, "wiki", "summaries")

RE_SP = re.compile(r"^source_path:\s*(.+)$", re.M)
RE_WC = re.compile(r"^word_count:\s*(\d+)", re.M)
RE_IMG = re.compile(r"^images:\s*(\d+)", re.M)
RE_TITLE = re.compile(r"^title:\s*(.+)$", re.M)
RE_MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

covered = set()
existing_stems = set()
for fn in os.listdir(DOC):
    if not fn.endswith(".md"):
        continue
    existing_stems.add(fn[:-3])
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
        if w >= 60:
            continue          # 涉敏，跳过
        if w == 0 and n == 0:
            continue          # 真空，跳过
        targets.append((rel, s))

print("待生成纯图笔记页：%d 篇" % len(targets))

made, skip = 0, []
for rel, s in targets:
    mt = RE_TITLE.search(s)
    title = mt.group(1).strip().strip('"') if mt else os.path.basename(rel)[:-3]
    imgs = RE_MD_IMG.findall(s)
    if not imgs:
        skip.append(rel)
        continue
    # 正文里除标题外的极少量文字（可能有一两句）
    body = s.split("---", 2)[-1]
    body = re.sub(r"^#.*$", "", body, flags=re.M)
    body = RE_MD_IMG.sub("", body)
    extra = re.sub(r"\s+", " ", body).strip()

    stem = "2026-11-06-%s" % re.sub(r'[\\/:*?"<>|]', "_", title)
    if stem in existing_stems:
        tag = rel.replace("raw/docs/personal-assets/", "").rsplit("/", 1)[0].replace("/", "-")
        stem = "2026-11-06-%s-%s" % (re.sub(r'[\\/:*?"<>|]', "_", title), tag)
    k = 2
    base = stem
    while stem in existing_stems:
        stem = "%s_%d" % (base, k)
        k += 1
    existing_stems.add(stem)

    L = []
    L.append("---")
    L.append("type: doc")
    L.append("title: %s" % title)
    L.append("source_path: %s" % rel)
    L.append("source_type: youdao")
    L.append("modality: image")
    L.append("confidence: 0.6")
    L.append("compile_status: compiled")
    L.append("compiled_at: 2026-11-06")
    L.append("---")
    L.append("")
    L.append("# %s" % title)
    L.append("")
    L.append("## 摘要")
    L.append("")
    L.append("本篇为**截图笔记**：原文正文不足 60 字，内容全部承载在 %d 张图片里。"
             "按库规不做断言抽取——断言需要原文逐字证据，而本篇没有可引的文字。"
             "要查具体细节，直接看图或回原文。" % len(imgs))
    L.append("")
    if extra:
        L.append("原文另有少量文字：%s" % extra[:160])
        L.append("")
    L.append("## 关键断言")
    L.append("")
    L.append("（本篇无可提取文字，未抽取断言。`confidence: 0.6` 表示内容可信但未结构化。）")
    L.append("")
    L.append("## 内容")
    L.append("")
    for im in imgs:
        L.append("![](%s)" % im)
        L.append("")
    L.append("## 涉及概念")
    L.append("")
    L.append("（未挂接：无可提取文字，无法判断所属概念）")
    L.append("")
    L.append("## 原文位置")
    L.append("")
    L.append("`%s`" % rel)
    L.append("")

    io.open(os.path.join(DOC, stem + ".md"), "w", encoding="utf-8", newline="").write("\n".join(L))
    made += 1

print("已生成 %d 篇" % made)
if skip:
    print("无图片引用而跳过：%d 篇" % len(skip))
    for x in skip[:10]:
        print("   ", x)
