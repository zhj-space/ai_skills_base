"""整体遗留项核查：路径一致性、数据缺口、环境状态。

用 Write 落文件执行（heredoc 会破坏正则里的转义）。
"""
import io
import os
import re
import json
import collections

ROOT = r"D:/workspace/ai_kb_base"
KB = os.path.join(ROOT, "second-brain")
TOOLS = os.path.join(ROOT, "_tools")
SKILLS = os.path.join(ROOT, "llm-wiki-skills")


def read(p):
    return io.open(p, encoding="utf-8").read()


print("=" * 62)
print("① 规则文件 / 技能里引用的路径是否真实存在")
print("=" * 62)

# 只检查能明确判断存在性的路径片段；含尖括号或通配的是占位，跳过
PAT = re.compile(r"`([A-Za-z0-9_\-./]+\.(?:md|py|json)|(?:wiki|raw|_tools|_templates|attachments)/[A-Za-z0-9_\-./]*)`")


def check_paths(label, files):
    bad = []
    total = 0
    for p in files:
        if not os.path.exists(p):
            continue
        s = read(p)
        for m in PAT.finditer(s):
            frag = m.group(1).strip()
            if "<" in frag or "|" in frag or "*" in frag:
                continue
            total += 1
            cands = [
                os.path.join(KB, frag), os.path.join(ROOT, frag),
                os.path.join(KB, "wiki", frag), os.path.join(TOOLS, frag),
            ]
            if not any(os.path.exists(c) for c in cands):
                bad.append((os.path.basename(p), frag))
    print("%-22s 检查 %3d 处引用，失效 %d 处" % (label, total, len(bad)))
    seen = set()
    for f, frag in bad:
        if (f, frag) in seen:
            continue
        seen.add((f, frag))
        print("    !! %-16s -> %s" % (f, frag))
    return bad


check_paths("agent.md", [os.path.join(KB, "agent.md")])
skill_files = []
for r, _, fs in os.walk(SKILLS):
    for f in fs:
        if f.endswith(".md"):
            skill_files.append(os.path.join(r, f))
check_paths("skills/*.md", skill_files)

print()
print("=" * 62)
print("② 脚本硬编码根路径")
print("=" * 62)
roots = collections.Counter()
for f in sorted(os.listdir(TOOLS)):
    if not f.endswith(".py"):
        continue
    s = read(os.path.join(TOOLS, f))
    for m in re.finditer(r'["\']([A-Za-z]:[/\\][^"\']*second-brain)["\']', s):
        roots[m.group(1)] += 1
for k, v in roots.items():
    print("  %-46s %d 个脚本" % (k, v))

print()
print("=" * 62)
print("③ 模板 / 结构一致性")
print("=" * 62)
tpl_dir = os.path.join(KB, "wiki", "_templates")
real_tpl = set(f for f in os.listdir(tpl_dir) if f.endswith(".md"))
agent = read(os.path.join(KB, "agent.md"))
ref_tpl = set(re.findall(r"_templates/([a-z-]+\.md)", agent))
print("模板文件 %d 个，agent.md 引用 %d 个" % (len(real_tpl), len(ref_tpl)))
print("  目录有但没被引用：" + (", ".join(sorted(real_tpl - ref_tpl)) or "无"))
print("  被引用但不存在：" + (", ".join(sorted(ref_tpl - real_tpl)) or "无"))

BASE_SEGS = ["是什么", "怎样理解 · 为什么", "有什么性质", "怎么用", "关系", "常见误区", "出处"]
seg_bad = []
for d, tp in (("concepts", "concept"), ("entities", "entity"),
              ("methods", "method"), ("metrics", "metric")):
    p = os.path.join(KB, "wiki", d)
    for f in os.listdir(p):
        if not f.endswith(".md"):
            continue
        s = read(os.path.join(p, f))
        segs = set(re.findall(r"^## (.+)$", s, re.M))
        miss = [b for b in BASE_SEGS if b not in segs]
        if miss:
            seg_bad.append((d, f[:-3], miss))
print("七段不全的节点页：%d" % len(seg_bad))
for d, n, m in seg_bad[:5]:
    print("    %s/%s 缺 %s" % (d, n, "、".join(m)))

print()
print("=" * 62)
print("④ 数据层缺口")
print("=" * 62)
DOC = os.path.join(KB, "wiki", "summaries")
doc_files = [f for f in os.listdir(DOC) if f.endswith(".md")]

# 4.1 无概念链接的文档页
no_link = 0
exempt = 0
for f in doc_files:
    s = read(os.path.join(DOC, f))
    seg = s.split("## 涉及概念")[1].split("\n## ")[0] if "## 涉及概念" in s else ""
    if "[[" in seg:
        continue
    no_link += 1
    if any(k in seg for k in ("已屏蔽", "未挂接", "无独立概念页")):
        exempt += 1
print("文档页 %d 篇，其中无概念链接 %d 篇（已声明豁免 %d，悬空 %d）"
      % (len(doc_files), no_link, exempt, no_link - exempt))

# 4.2 指标页口径
for f in os.listdir(os.path.join(KB, "wiki", "metrics")):
    if not f.endswith(".md"):
        continue
    s = read(os.path.join(KB, "wiki", "metrics", f))
    hit = [k for k in ("分子", "分母", "时间窗", "单位") if k in s]
    print("  指标 %-10s 口径四要素命中 %d/4 %s" % (f[:-3], len(hit), "、".join(hit)))

# 4.3 文档页 source_path 有效性
bad_sp = []
for f in doc_files:
    s = read(os.path.join(DOC, f))
    m = re.search(r"^source_path:[ \t]*(.+)$", s, re.M)
    if not m:
        bad_sp.append((f, "(缺)"))
        continue
    p = os.path.join(KB, m.group(1).strip().strip('"').replace("\\", "/"))
    if not os.path.exists(p):
        bad_sp.append((f, m.group(1).strip()))
print("source_path 失效：%d 篇" % len(bad_sp))
for f, p in bad_sp[:5]:
    print("    %s -> %s" % (f, p))

print()
print("=" * 62)
print("⑤ 环境与体积")
print("=" * 62)
gj = os.path.join(KB, ".obsidian", "graph.json")
d = json.load(io.open(gj, encoding="utf-8"))
print("graph.json: %d 个颜色组 · search 长度 %d · 只读=%s"
      % (len(d.get("colorGroups") or []), len(d.get("search") or ""),
         "是" if not os.access(gj, os.W_OK) else "否"))

for name in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, name)
    if os.path.isdir(p) and (name.startswith("_backup") or name.startswith("_archive")):
        size = sum(os.path.getsize(os.path.join(r, f))
                   for r, _, fs in os.walk(p) for f in fs if os.path.exists(os.path.join(r, f)))
        print("  备份 %-32s %.1f MB" % (name, size / 1024 / 1024))

for f in ("graph.html", "待办日志-2026-11-06.md", "换库报告-2026-11-06.md"):
    p = os.path.join(ROOT, f)
    print("  产物 %-32s %s" % (f, ("%.0f KB" % (os.path.getsize(p) / 1024)) if os.path.exists(p) else "不存在"))
