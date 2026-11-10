# -*- coding: utf-8 -*-
"""按 LLM-Wiki 社区惯例做 i18n 迁移：目录与属性全英文，页面标题保留中文。
已备份到 _backup_before_i18n_20261107/。
"""
import io
import os
import re
import shutil

KB = r"D:/workspace/ai_kb_base/second-brain"

# ── 1. 目录改名（自深向浅，保持层级深度，图片根路径不变） ──
DIRMAP = [
    ("raw/docs/personal-assets/AI相关", "raw/docs/personal-assets/ai"),
    ("raw/docs/personal-assets/个人提升", "raw/docs/personal-assets/growth"),
    ("raw/docs/personal-assets/创作", "raw/docs/personal-assets/creation"),
    ("raw/docs/personal-assets/前端", "raw/docs/personal-assets/frontend"),
    ("raw/docs/personal-assets/基础相关", "raw/docs/personal-assets/basics"),
    ("raw/docs/personal-assets/大数据", "raw/docs/personal-assets/bigdata"),
    ("raw/docs/personal-assets/开发总结", "raw/docs/personal-assets/devnotes"),
    ("raw/docs/personal-assets/投资", "raw/docs/personal-assets/investment"),
    ("raw/docs/personal-assets/操作系统", "raw/docs/personal-assets/os"),
    ("raw/docs/personal-assets/数学", "raw/docs/personal-assets/math"),
    ("raw/docs/personal-assets/数据库", "raw/docs/personal-assets/database"),
    ("raw/docs/personal-assets/方法论", "raw/docs/personal-assets/methodology"),
    ("raw/docs/personal-assets/机器学习", "raw/docs/personal-assets/ml"),
    ("raw/docs/personal-assets/架构与性能", "raw/docs/personal-assets/architecture"),
    ("raw/docs/personal-assets/灵感与研究", "raw/docs/personal-assets/research"),
    ("raw/docs/personal-assets/算法", "raw/docs/personal-assets/algorithm"),
    ("raw/docs/personal-assets/系统运维", "raw/docs/personal-assets/ops"),
    ("raw/docs/personal-assets/自媒体发布", "raw/docs/personal-assets/media"),
    ("raw/docs/personal-assets/项目实践", "raw/docs/personal-assets/practice"),
    ("raw/docs/personal-assets/项目管理", "raw/docs/personal-assets/pm"),
    ("raw/docs/个人资产体系", "raw/docs/personal-assets"),
    ("raw/文档", "raw/docs"),
    ("raw/网页", "raw/web"),
    ("raw/视频", "raw/video"),
    ("raw/其他", "raw/other"),
    ("raw", "raw"),
    ("wiki/_模板", "wiki/_templates"),
    ("wiki/文档", "wiki/summaries"),
    ("wiki/沉淀", "wiki/analysis"),
    ("wiki/概念", "wiki/concepts"),
]

for old, new in DIRMAP:
    a, b = os.path.join(KB, old), os.path.join(KB, new)
    if os.path.isdir(a) and not os.path.exists(b):
        os.rename(a, b)
        print("DIR  %-40s -> %s" % (old, new))
    elif os.path.isdir(b):
        print("SKIP %-40s 已存在" % new)

# ── 2. 概念页按 entity_type 拆到 concepts/entities/methods/metrics ──
CD = os.path.join(KB, "wiki", "concepts")
SUB = {"concept": "concepts", "entity": "entities", "method": "methods", "metric": "metrics"}
V2E = {"concepts": "concept", "实体": "entity", "方法": "method", "指标": "metric"}
moved = 0
for f in sorted(os.listdir(CD)):
    if not f.endswith(".md"):
        continue
    s = io.open(os.path.join(CD, f), encoding="utf-8").read()
    m = re.search(r"^entity_type:[ \t]*(\S+)", s, re.M)
    raw = m.group(1) if m else ""
    key = V2E.get(raw, raw)
    sub = SUB.get(key, "concepts")
    if sub == "concepts":
        continue
    dst = os.path.join(KB, "wiki", sub)
    os.makedirs(dst, exist_ok=True)
    shutil.move(os.path.join(CD, f), os.path.join(dst, f))
    moved += 1
print("SPLIT 移到 entities/methods/metrics 共 %d 页" % moved)

# ── 3. 文件名改名 ──
FILEMAP = [
    ("wiki/topic-map.md", "wiki/topic-map.md"),
    ("wiki/topic-map.md", "wiki/topic-map.md"),
    ("wiki/analysis/digest-index.md", "wiki/analysis/digest-index.md"),
    ("agent.md", "agent.md"),
]
for old, new in FILEMAP:
    a, b = os.path.join(KB, old), os.path.join(KB, new)
    if os.path.exists(a) and not os.path.exists(b) and old != new:
        os.rename(a, b)
        print("FILE %-36s -> %s" % (old, new))

TP = os.path.join(KB, "wiki", "_templates")
TMAP = {"文档页模板.md": "doc-template.md", "概念模板.md": "concept-template.md",
        "沉淀模板.md": "digest-template.md", "主题地图模板.md": "topic-template.md"}
for f in os.listdir(TP):
    if f in TMAP:
        os.rename(os.path.join(TP, f), os.path.join(TP, TMAP[f]))
        print("TPL  %-22s -> %s" % (f, TMAP[f]))

# ── 4. 全库文本替换：路径 + 属性值 + 关系词 ──
PATHS = [
    ("raw/docs/personal-assets/", "raw/docs/personal-assets/"),
    ("raw/docs/personal-assets/", "raw/docs/personal-assets/"),
    ("raw/docs/", "raw/docs/"),
    ("raw/docs/", "raw/docs/"),
    ("raw/web/", "raw/web/"),
    ("raw/video/", "raw/video/"),
    ("raw/other/", "raw/other/"),
    ("raw/", "raw/"),
    ("wiki/concepts/", "wiki/concepts/"),
    ("wiki/summaries/", "wiki/summaries/"),
    ("wiki/analysis/", "wiki/analysis/"),
    ("wiki/_templates/", "wiki/_templates/"),
]
VALUES = [
    ("entity_type: node", "entity_type: node"),
    ("entity_type: entity", "entity_type: entity"),
    ("entity_type: method", "entity_type: method"),
    ("entity_type: metric", "entity_type: metric"),
    ("type: node", "type: node"),
    ("type: digest", "type: digest"),
]
LINKS = [
    ("[[topic-map]]", "[[topic-map]]"),
    ("[[digest-index]]", "[[digest-index]]"),
    ("topic-map.md", "topic-map.md"),
    ("digest-index.md", "digest-index.md"),
    ("agent.md", "agent.md"),
]
# 关系词：只替换行首的 `- 词：`
RELS = [
    ("上位", "broader"), ("下位", "narrower"),
    ("实例化", "has_instance"), ("实例", "instance_of"),
    ("组成", "has_part"), ("部分于", "part_of"),
    ("前置", "requires"), ("后继", "enables"),
    ("产出", "produces"), ("由产出", "produced_by"),
    ("应用", "applies_to"), ("被应用", "applied_by"),
    ("演进", "evolves_to"), ("前身", "evolved_from"),
    ("相关", "related_to"), ("出处文档", "source"),
]
REL_RE = re.compile(r"^(-\s*)(" + "|".join(k for k, _ in RELS) + r")([：:])")
REL_D = dict(RELS)

targets = []
for r, _, fs in os.walk(KB):
    for f in fs:
        if f.endswith((".md", ".json")):
            targets.append(os.path.join(r, f))
for f in sorted(os.listdir(r"D:/workspace/ai_kb_base/_tools")):
    if f.endswith(".py"):
        targets.append(os.path.join(r"D:/workspace/ai_kb_base/_tools", f))

n = 0
for p in targets:
    try:
        s0 = io.open(p, encoding="utf-8").read()
    except Exception:
        continue
    s = s0
    for a, b in PATHS + VALUES + LINKS:
        s = s.replace(a, b)
    out = []
    for ln in s.split("\n"):
        m = REL_RE.match(ln)
        if m:
            ln = m.group(1) + REL_D[m.group(2)] + m.group(3) + ln[m.end():]
        out.append(ln)
    s = "\n".join(out)
    if s != s0:
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        n += 1
print("TEXT 改写 %d 个文件" % n)
