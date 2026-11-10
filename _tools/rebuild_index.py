# -*- coding: utf-8 -*-
"""重建 index.md 的概念页 / 文档页两个列表，按名称排序，计数自动算"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
IDX = os.path.join(KB, "index.md")


def first_sentence(text, limit=90):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    return text[:limit]


def read_concepts():
    d = os.path.join(KB, "wiki", "concepts")
    out = []
    for fn in os.listdir(d):
        if not fn.endswith(".md"):
            continue
        s = io.open(os.path.join(d, fn), encoding="utf-8").read()
        name = fn[:-3]
        # 取 blockquote 那句定义
        m = re.search(r"^# .+\n+\s*>\s*(.+)$", s, re.M)
        desc = first_sentence(m.group(1)) if m else ""
        out.append((name, desc))
    return sorted(out, key=lambda x: x[0])


def read_docs():
    d = os.path.join(KB, "wiki", "summaries")
    out = []
    for fn in os.listdir(d):
        if not fn.endswith(".md"):
            continue
        # 凭据屏蔽页不进索引、不进检索（库规）
        if "凭据已屏蔽" in fn:
            continue
        s = io.open(os.path.join(d, fn), encoding="utf-8").read()
        t = re.search(r"^title:\s*(.+)$", s, re.M)
        title = t.group(1).strip().strip('"') if t else fn[:-3]
        m = re.search(r"## 摘要\s*\n+(.+?)(?:\n\n|\n##)", s, re.S)
        desc = first_sentence(m.group(1)) if m else ""
        out.append((fn[:-3], title, desc))
    return sorted(out, key=lambda x: x[0])


C = read_concepts()
D = read_docs()

concept_block = ["## 概念页（%d）" % len(C), ""]
for name, desc in C:
    concept_block.append("- [[%s]] — %s" % (name, desc) if desc else "- [[%s]]" % name)

doc_block = ["## 文档页（%d）" % len(D), ""]
for stem, title, desc in D:
    if desc:
        doc_block.append("- [[%s|%s]] — %s" % (stem, title, desc))
    else:
        doc_block.append("- [[%s|%s]]" % (stem, title))

s = io.open(IDX, encoding="utf-8").read()

# 替换概念页节
s = re.sub(r"## 概念页（\d+）\n\n(?:- .*\n)+", "\n".join(concept_block) + "\n", s)
# 替换文档页节
s = re.sub(r"## 文档页（\d+）\n\n(?:- .*\n)+", "\n".join(doc_block) + "\n", s)

io.open(IDX, "w", encoding="utf-8", newline="").write(s)
print("概念页 %d 条 / 文档页 %d 条 已写入 index.md" % (len(C), len(D)))
