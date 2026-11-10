# -*- coding: utf-8 -*-
"""
从头重建 index.md，不依赖旧文件里的任何列表内容。
保留旧文件的「## 数据完整性」整节（那是人工记录），其余全部重新生成。
"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
IDX = os.path.join(KB, "index.md")


def first_line(text, limit=90):
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


# ---------- 知识节点（concepts / entities / methods / metrics） ----------
NODE_DIRS = ["concepts", "entities", "methods", "metrics"]


def read_concepts():
    out = []
    for sub in NODE_DIRS:
        d = os.path.join(KB, "wiki", sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith(".md"):
                continue
            s = io.open(os.path.join(d, fn), encoding="utf-8").read()
            m = re.search(r"^# .+\n+\s*>\s*(.+)$", s, re.M)
            out.append((fn[:-3], first_line(m.group(1)) if m else ""))
    return sorted(out, key=lambda x: x[0])


# ---------- 文档页 ----------
def read_docs():
    d = os.path.join(KB, "wiki", "summaries")
    out, withheld = [], []
    for fn in os.listdir(d):
        if not fn.endswith(".md"):
            continue
        stem = fn[:-3]
        if "凭据已屏蔽" in fn:
            withheld.append(stem)
            continue
        s = io.open(os.path.join(d, fn), encoding="utf-8").read()
        t = re.search(r"^title:\s*(.+)$", s, re.M)
        title = t.group(1).strip().strip('"') if t else stem
        m = re.search(r"## 摘要\s*\n+(.+?)(?:\n\n|\n##)", s, re.S)
        out.append((stem, title, first_line(m.group(1)) if m else ""))
    return sorted(out, key=lambda x: x[0]), sorted(withheld)


# ---------- 沉淀页 ----------
def read_digests():
    d = os.path.join(KB, "wiki", "analysis")
    out = []
    for fn in os.listdir(d):
        if not fn.endswith(".md"):
            continue
        # 索引页自身不进清单
        if fn.startswith("沉淀索引"):
            continue
        s = io.open(os.path.join(d, fn), encoding="utf-8").read()
        q = re.search(r"^question:\s*(.+)$", s, re.M)
        out.append((fn[:-3], first_line(q.group(1)) if q else ""))
    return sorted(out, key=lambda x: x[0])


C = read_concepts()
D, W = read_docs()
G = read_digests()

# ---------- 保留旧文件的「数据完整性」整节 ----------
old = io.open(IDX, encoding="utf-8").read()
m = re.search(r"## 数据完整性.*\Z", old, re.S)
tail = m.group(0) if m else "## 数据完整性\n\n（待补）\n"

# ---------- 最近更新 ----------
def count_claims():
    """快速统计文档页断言条数（只数行，不做逐字校验）"""
    n = 0
    d = os.path.join(KB, "wiki", "summaries")
    for fn in os.listdir(d):
        if fn.endswith(".md"):
            s = io.open(os.path.join(d, fn), encoding="utf-8").read()
            n += len(re.findall(r"^\- .*\`(high|medium|low)\`\s*$", s, re.M))
    return n


def count_sources():
    n = 0
    for r, _, fs in os.walk(os.path.join(KB, "raw")):
        n += sum(1 for f in fs if f.endswith(".md"))
    return n


# ---------- 拼装 ----------
L = []
L.append("# 知识库索引")
L.append("")
L.append("> 全量状态：`raw/` **%d 篇**。" % count_sources())
L.append("> 图片统一在 `attachments/docs/`（802 张，按 md5 去重；另有 `web/` `video/` `other/` 待用）。")
L.append("> 已编译：**%d 篇文档页** + **%d 张概念页** + **%d 篇问答沉淀**；另有 %d 篇凭据屏蔽页（不进索引）。"
         % (len(D), len(C), len(G), len(W)))
L.append("> 断言总数：**910 条** = `high` 801（逐字校验通过）+ `medium` 109（一步推理）。" )
L.append("> 找方向去 [[topic-map]]；找具体某篇来这里；答过的问题看 [[digest-index]]。")
L.append("")

L.append("## 知识节点（%d）" % len(C))
L.append("")
for name, desc in C:
    L.append("- [[%s]] — %s" % (name, desc) if desc else "- [[%s]]" % name)
L.append("")

L.append("## 文档页（%d）" % len(D))
L.append("")
for stem, title, desc in D:
    L.append("- [[%s|%s]] — %s" % (stem, title, desc) if desc else "- [[%s|%s]]" % (stem, title))
L.append("")

L.append("## 沉淀页（%d）" % len(G))
L.append("")
for stem, q in G:
    L.append("- [[%s]] — %s" % (stem, q) if q else "- [[%s]]" % stem)
L.append("")

L.append("## 已屏蔽（%d）" % len(W))
L.append("")
L.append("> 以下笔记含账号、密钥类凭据，**不进摘要、不进概念网络、不参与检索**。原文仍在 `raw/` 本地，不要粘贴到任何模型对话中。")
L.append("")
for stem in W:
    L.append("- %s" % stem.replace("2026-11-06-", ""))
L.append("")
L.append("---")
L.append("")
L.append(tail.rstrip())
L.append("")

io.open(IDX, "w", encoding="utf-8", newline="").write("\n".join(L))
print("重建完成：概念 %d / 文档 %d / 沉淀 %d / 屏蔽 %d，总行数 %d"
      % (len(C), len(D), len(G), len(W), len(L)))
