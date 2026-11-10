# -*- coding: utf-8 -*-
"""本体校验器：按 ontology.json 检查 wiki/概念 下的类、关系、别名。
用法：python check_ontology.py [--verbose]
只读，不改任何文件。
"""
import io
import os
import re
import json
import sys

KB = os.environ.get("KB_ROOT") or r"D:/workspace/ai_kb_base/second-brain"
NODE_DIRS = ["concepts", "entities", "methods", "metrics"]
CD = [os.path.join(KB, "wiki", d) for d in NODE_DIRS]
DD = os.path.join(KB, "wiki", "summaries")
GD = os.path.join(KB, "wiki", "analysis")
ONTO = os.path.join(KB, "ontology.json")
VERBOSE = "--verbose" in sys.argv

onto = json.load(io.open(ONTO, encoding="utf-8"))
REL = onto["relations"]
CLASSES = onto["classes"]

# 关系词表：正式词 + legacy 别名 → 规范词
VOCAB = {}
for canon, spec in REL.items():
    VOCAB[canon] = canon
    for a in spec.get("legacy_aliases", []):
        VOCAB[a] = canon


def pages(d):
    if not os.path.isdir(d):
        return []
    return sorted(f[:-3] for f in os.listdir(d) if f.endswith(".md"))


CON = sorted(sum((pages(d) for d in CD), []))
DOC, DIG = pages(DD), pages(GD)
ALL = set(CON) | set(DOC) | set(DIG)


def read(p):
    return io.open(p, encoding="utf-8").read()


def frontmatter(s):
    if not s.startswith("---"):
        return {}
    block = s.split("---", 2)[1]
    out = {}
    for ln in block.split("\n"):
        if ":" in ln and not ln.strip().startswith("#"):
            k, v = ln.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def section(s, name):
    if name not in s:
        return ""
    return s.split(name, 1)[1].split("\n## ", 1)[0]


CPATH = {}
for _d in CD:
    for _f in pages(_d):
        CPATH[_f] = os.path.join(_d, _f + ".md")

pages_data = {}
for c in CON:
    s = read(CPATH[c])
    fm = frontmatter(s)
    rels = []
    for ln in section(s, "## 关系").split("\n"):
        t = ln.strip()
        if not t.startswith("- "):
            continue
        m = re.match(r"^-\s*([^：:]{1,24})\s*[：:]", t)
        if not m:
            continue
        label = m.group(1).strip()
        targets = re.findall(r"\[\[([^\]|#]+)", t)
        rels.append((label, targets, t))
    # body = 正文全文（frontmatter 之后、出处段之前）。
    # 不按固定段名拼接 —— 四类模板的段名不同，写死会让 C8 空跑。
    _body = s.split("## 出处")[0] if "## 出处" in s else s
    _body = re.sub(r"^---\n.*?\n---\n", "", _body, flags=re.S)

    pages_data[c] = {
        "type": fm.get("type", "").strip(),
        "entity_type": fm.get("entity_type", "").strip(),
        "aliases": [a.strip() for a in fm.get("aliases", "").strip("[]").split(",") if a.strip()],
        "rels": rels,
        "how": section(s, "## 怎么用"),
        "body": _body,
    }

doc_type = {}
for d in DOC:
    doc_type[d] = frontmatter(read(os.path.join(DD, d + ".md"))).get("type", "")

issues = {"C1": [], "C2": [], "C3": [], "C4": [], "C5": [], "C6": [], "C7": [],
          "C8": [], "C9": [], "C10": [], "D1": [], "G1": []}

# C1 目标存在 + 出处文档只指文档页
for c, d in pages_data.items():
    for label, targets, line in d["rels"]:
        canon = VOCAB.get(label, label)
        for t in targets:
            if t not in ALL:
                issues["C1"].append("%s ──%s──> %s（不存在）" % (c, label, t))
            elif canon == "出处文档" and t not in DOC:
                issues["C1"].append("%s ──出处文档──> %s（不是文档页）" % (c, t))

# C2 互为同一关系
for c, d in pages_data.items():
    for label, targets, line in d["rels"]:
        canon = VOCAB.get(label, label)
        spec = REL.get(canon, {})
        if spec.get("symmetric") or canon == "出处文档":
            continue
        for t in targets:
            if t not in pages_data:
                continue
            for l2, t2, _ in pages_data[t]["rels"]:
                if t2 and l2 == label and c in t2:
                    issues["C2"].append("%s ⇄ %s 互标「%s」" % (c, t, label))

# C3 前置环（边方向：X 是 Y 的前置 → X → Y）
edges = {}
for c, d in pages_data.items():
    for label, targets, line in d["rels"]:
        canon = VOCAB.get(label, label)
        for t in targets:
            if t not in pages_data:
                continue
            if canon == "requires":
                edges.setdefault(t, set()).add(c)   # t 是本页前置
            elif canon == "enables":
                edges.setdefault(c, set()).add(t)   # 本页是 t 的前置


def find_cycles(g):
    color = {}
    stack = []
    found = []

    def dfs(u):
        color[u] = 1
        stack.append(u)
        for v in g.get(u, ()):
            if color.get(v, 0) == 1:
                i = stack.index(v)
                found.append(" → ".join(stack[i:] + [v]))
            elif color.get(v, 0) == 0:
                dfs(v)
        stack.pop()
        color[u] = 2

    for n in list(g):
        if color.get(n, 0) == 0:
            dfs(n)
    return found


for cyc in find_cycles(edges):
    issues["C3"].append("前置环：" + cyc)

# C4 类与关系合法（按 type 判类）
for c, d in pages_data.items():
    et = d["type"]
    if et == "entity":
        for label, targets, _ in d["rels"]:
            if VOCAB.get(label, label) == "produces":
                for t in targets:
                    if pages_data.get(t, {}).get("type") == "metric":
                        issues["C4"].append("%s (entity) produces metric %s" % (c, t))
    if et == "method":
        steps = len(re.findall(r"^\s*\d+[.、]", d["how"], re.M))
        if steps < 3:
            issues["C4"].append("%s (method) has only %d steps" % (c, steps))

# C5 关系词是否在词表
legacy = {}
for c, d in pages_data.items():
    for label, targets, _ in d["rels"]:
        if label not in VOCAB:
            issues["C5"].append("%s 用了未登记关系词「%s」" % (c, label))
        elif VOCAB[label] != label:
            legacy[label] = legacy.get(label, 0) + 1

# C6 别名唯一
seen = {}
for c, d in pages_data.items():
    for a in d["aliases"] + [c]:
        if a in seen and seen[a] != c:
            issues["C6"].append("「%s」同时属于 %s 与 %s" % (a, seen[a], c))
        seen.setdefault(a, c)

# C7 关系端点类组合必须在 allowed 内（按 type 取类）
for c, d in pages_data.items():
    fc = d["type"]
    for label, targets, _ in d["rels"]:
        canon = VOCAB.get(label, label)
        allowed = REL.get(canon, {}).get("allowed")
        if not allowed:
            continue
        for t in targets:
            if t not in pages_data:
                continue
            tc = pages_data[t]["type"]
            if [fc, tc] not in allowed:
                issues["C7"].append("%s（%s）──%s──> %s（%s）"
                                    % (c, fc, label, t, tc))

# C8 实体页须回答版本 / 可替代，或显式声明缺口
C8_HIT = onto["constraints"]["C8"]["hit"]
for c, d in pages_data.items():
    if d["type"] != "entity":
        continue
    body = d["body"]
    if not any(h in body for h in C8_HIT) and not re.search(r"\bv\d\b|v\d+\.", body):
        issues["C8"].append("%s：未写版本，也未写可替代或信息缺口" % c)

# C9 实体页不能只有「相关」（关系段须有 ≥1 条结构关系）
WEAK = set(onto["constraints"]["C9"]["weak"])
for c, d in pages_data.items():
    if d["type"] != "entity":
        continue
    labels = set(VOCAB.get(label, label) for label, _, _ in d["rels"])
    if not (labels - WEAK):
        issues["C9"].append("%s：关系段只有 %s" % (c, "、".join(sorted(labels)) or "空"))

# C10 entity_type 只能在 type == entity 的页面出现，且值须已登记
SUBTYPES = set(k for k in onto["entity_subtypes"] if not k.startswith("_"))
VALID_TYPE = set(onto["classes"].keys()) | {"doc", "digest", "index"}
for c, d in pages_data.items():
    tp, sub = d["type"], d["entity_type"]
    if tp not in VALID_TYPE:
        issues["C10"].append("%s：type「%s」未登记（应为 %s）"
                             % (c, tp or "空", "/".join(sorted(VALID_TYPE)))) 
    elif tp != "entity" and sub:
        issues["C10"].append("%s（type=%s）：不该有 entity_type「%s」" % (c, tp, sub))
    elif tp == "entity":
        if not sub:
            issues["C10"].append("%s：实体页缺 entity_type 子类" % c)
        elif sub not in SUBTYPES:
            issues["C10"].append("%s：实体子类「%s」未登记" % (c, sub))

# C10 第二段：wiki 下所有非节点页（summaries / analysis / topic-map）的 type 也须已登记
NODE_DIR_SET = set(os.path.abspath(d) for d in CD)
for _root, _dirs, _files in os.walk(os.path.join(KB, "wiki")):
    if os.path.abspath(_root) in NODE_DIR_SET or "_templates" in _root:
        continue
    for _f in _files:
        if not _f.endswith(".md"):
            continue
        _tp = frontmatter(read(os.path.join(_root, _f))).get("type", "").strip()
        if _tp not in VALID_TYPE:
            issues["C10"].append("%s：type「%s」未登记" % (_f[:-3], _tp or "空"))

# D1 文档页「涉及概念」不得为空（须给链接或豁免理由）
EX_D = onto["constraints"]["D1"]["exempt_if"]
for dname in DOC:
    s = read(os.path.join(DD, dname + ".md"))
    seg = section(s, "## 涉及概念").strip()
    if not seg:
        issues["D1"].append("%s：涉及概念为空" % dname)
    elif "[[" not in seg and not any(k in seg for k in EX_D):
        issues["D1"].append("%s：既无链接也无豁免理由" % dname)

# G1 沉淀页 based_on 须指向现存概念页
EX_G = onto["constraints"]["G1"]["exempt_if"]
for gname in DIG:
    if any(k in gname for k in EX_G):
        continue
    s = read(os.path.join(GD, gname + ".md"))
    m = re.search(r"^based_on:[ \t]*(.+)$", s, re.M)
    if not m:
        issues["G1"].append("%s：无 based_on" % gname)
        continue
    refs = re.findall(r"\[\[([^\]|#]+)", m.group(1))
    if not refs:
        refs = [x.strip() for x in m.group(1).strip().strip("[]").split(",") if x.strip()]
    bad = [r for r in refs if r not in pages_data]
    if bad:
        issues["G1"].append("%s：based_on 指向不存在 %s" % (gname, "、".join(bad)))

print("=== 本体校验（ontology.json v%d）===" % onto["version"])
print("知识节点 %d · 关系条目 %d · 关系词表 %d"
      % (len(CON), sum(len(d["rels"]) for d in pages_data.values()), len(VOCAB)))

dist = {}
for d in pages_data.values():
    dist[d["type"] or "(未标)"] = dist.get(d["type"] or "(未标)", 0) + 1
print("类分布（按 type）：" + " · ".join("%s %d" % (k, v) for k, v in sorted(dist.items(), key=lambda x: -x[1])))
idle = [k for k in CLASSES if dist.get(k, 0) == 0]
if idle:
    print("⚠ 空类：%s —— 相关约束不会触发，需先修正类型标注" % " · ".join(idle))

sub = {}
for d in pages_data.values():
    if d["type"] == "entity":
        sub[d["entity_type"] or "(未标)"] = sub.get(d["entity_type"] or "(未标)", 0) + 1
if sub:
    print("实体子类（entity_type）：" + " · ".join("%s %d" % (k, v) for k, v in sorted(sub.items(), key=lambda x: -x[1])))
    unused = sorted(SUBTYPES - set(sub))
    if unused:
        print("  已登记未使用：%s" % " · ".join(unused))
print()

for cid in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "D1", "G1"):
    lst = issues[cid]
    rule = onto["constraints"][cid]["rule"]
    lvl = onto["constraints"][cid]["level"]
    print("%s [%s] %-46s %3d" % (cid, lvl, rule[:44], len(lst)))
    if lst:
        show = lst if VERBOSE else lst[: (8 if cid == "C5" else 6)]
        for x in show:
            print("      " + x)
        if len(lst) > len(show):
            print("      …… 另有 %d 处（--verbose 看全部）" % (len(lst) - len(show)))
print()

if legacy:
    print("可自动归一的旧关系词：")
    for k, v in sorted(legacy.items(), key=lambda x: -x[1]):
        print("   %-8s → %-6s %2d 处" % (k, VOCAB[k], v))
    print()

err = sum(len(issues[k]) for k in issues if onto["constraints"][k]["level"] == "error")
warn = sum(len(issues[k]) for k in issues if onto["constraints"][k]["level"] == "warn")
print("合计：error %d 处 · warn %d 处" % (err, warn))
