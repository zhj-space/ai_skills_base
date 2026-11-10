# -*- coding: utf-8 -*-
"""
构建新的 raw/文档：
  - 已有篇：复用旧 front-matter（note_id 等），更新状态与字数，正文换新版
  - 新增篇：生成新 front-matter
  - 图片：整体复制
输出到 _build_sources_文档，校验通过后再替换
"""
import os, re, io, shutil

NEW = r"D:/workspace/ai_kb_base/_ynote_export/个人资产体系"
OLD = r"D:/workspace/ai_kb_base/second-brain/raw/docs/个人资产体系"
BUILD = r"D:/workspace/ai_kb_base/_build_sources_文档/个人资产体系"

def parse_fm(s):
    m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
    fm, body = {}, s
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        body = s[m.end():]
    return fm, body

def strip_h1(s):
    """去掉正文开头的 H1，返回 (title 或 None, 剩余正文)"""
    t = s.lstrip("\n")
    m = re.match(r"^#\s+(.+?)\s*\n", t)
    if m:
        return m.group(1).strip(), t[m.end():].lstrip("\n")
    return None, t

def count_words(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[#*`>|~\-=]", "", s)
    s = re.sub(r"\s+", "", s)
    return len(s)

def yq(v):
    v = str(v)
    if re.search(r"[:#\[\]{}]|^[\s\"']|[\s\"']$", v):
        return '"' + v.replace('"', '\\"') + '"'
    return v

stats = {"update": 0, "new": 0, "skip": 0}
report = []

for root, _, files in os.walk(NEW):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        src = os.path.join(root, fn)
        rel = os.path.relpath(src, NEW)
        dst = os.path.join(BUILD, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        raw = io.open(src, encoding="utf-8").read()
        h1, body = strip_h1(raw)
        body = body.strip() + "\n"

        oldp = os.path.join(OLD, rel)
        if os.path.exists(oldp):
            ofm, _ = parse_fm(io.open(oldp, encoding="utf-8").read())
            stats["update"] += 1
        else:
            ofm = {}
            stats["new"] += 1

        title = ofm.get("title") or h1 or os.path.splitext(fn)[0]
        notebook = "个人资产体系/" + os.path.dirname(rel).replace("\\", "/")
        notebook = notebook.rstrip("/")
        nimg = len(re.findall(r"!\[[^\]]*\]\(images/", body))
        if nimg and count_words(body) < 60:
            modality = "image"
        elif nimg:
            modality = "text+image"
        else:
            modality = "text"

        fm_lines = [
            "---",
            "note_id: %s" % yq(ofm.get("note_id", "")),
            "title: %s" % yq(title),
            "notebook: %s" % yq(notebook),
            "source_type: youdao",
            "modality: %s" % modality,
            "captured_at: %s" % ofm.get("captured_at", "2026-11-06"),
            "content_status: ok",
            "confidence: %s" % ("0.95" if ofm.get("confidence") in (None, "0.0", "") else ofm.get("confidence")),
            "word_count: %d" % count_words(body),
            "images: %d" % nimg,
            "---",
            "",
            "# %s" % title,
            "",
        ]
        io.open(dst, "w", encoding="utf-8", newline="").write("\n".join(fm_lines) + body)
        report.append((rel, modality, nimg, count_words(body)))

# 复制图片目录
imgcopied = 0
for root, dirs, _ in os.walk(NEW):
    if "images" in dirs:
        s = os.path.join(root, "images")
        rel = os.path.relpath(s, NEW)
        d = os.path.join(BUILD, rel)
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)
        imgcopied += len(os.listdir(d))

print("更新 %d 篇 / 新增 %d 篇 / 图片 %d 张" % (stats["update"], stats["new"], imgcopied))
print("\n=== modality 分布 ===")
from collections import Counter
for k, v in Counter(x[1] for x in report).most_common():
    print("  %-12s %d" % (k, v))
print("\n=== 新增篇清单 ===")
for rel, md, n, w in report:
    if not os.path.exists(os.path.join(OLD, rel)):
        print("  [%s] %4d字 %d图  %s" % (md, w, n, rel))
