# -*- coding: utf-8 -*-
"""按概念模板生成数学概念页"""
import io, json, os
from chap_tail import is_chap_tail

KB = r"D:/workspace/ai_kb_base/second-brain"
TOOLS = r"D:/workspace/ai_kb_base/_tools"
OUT_DIR = os.path.join(KB, "wiki", "concepts")

data = {}
for fn in ("math_concepts_a.json", "math_concepts_b.json", "math_concepts_c.json"):
    data.update(json.load(io.open(os.path.join(TOOLS, fn), encoding="utf-8")))

ITEMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_items.json"), encoding="utf-8"))
BY_NO = {it["no"]: it for it in ITEMS}
CLAIMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_claims.json"), encoding="utf-8"))

# 原文定位标签词表（最长匹配，避免把名称切断）
TAGS = sorted(["定理链起点","定理链终点","微分学中枢","存在性工具","结构性质","计算模板","图形语言",
               "概念升华","积分类型","核心定理","计算方法","系统方法","关键桥梁","全书之桥","公式源头",
               "语言基石","核心概念","计算核心","核心技巧","核心方法","高频工具","计算工具","综合应用",
               "基本概念","几何语言","本章核心","公式组","核心","重点","技术","理论","推广","拓展"],
              key=len, reverse=True)

def split_name(raw):
    for t in TAGS:
        if raw.endswith(t) and len(raw) > len(t):
            return raw[:-len(t)], t
    return raw, ""

# 概念页 -> 原文条目号：决定「核心定义与公式」「定理与运算律」两节的内容来源
MAP = {
 "极限": ["1.1","1.2","1.3","1.4"],
 "连续与间断": ["1.5","1.6"],
 "导数与微分": ["2.1","2.2","2.3","2.4"],
 "中值定理": ["3.1","3.2","3.3"],
 "泰勒公式": ["3.4"],
 "不定积分": ["4.1","4.2","4.3","4.4"],
 "定积分": ["5.1","5.2","5.5"],
 "牛顿-莱布尼茨公式": ["5.3","5.4"],
 "微元法": ["6.1","6.2","6.3"],
 "微分方程": ["7.1","7.2","7.3","7.4"],
 "向量代数": ["8.1","8.2","8.3","8.4"],
 "偏导数与全微分": ["9.1","9.2","9.3","9.4"],
 "梯度": ["9.5","9.6"],
 "重积分": ["10.1","10.2","10.3","10.4"],
 "曲线曲面积分": ["11.1","11.2","11.5"],
 "格林高斯斯托克斯公式": ["11.3","11.4","11.6"],
 "无穷级数": ["12.1","12.2","12.3","12.4","12.5"],
}

def render_block(nos, kind, title, prefix=None):
    """prefix 为 'P'/'U' 时给列表项加知识点编号；章末总结不计入编号"""
    out = [title, ""]
    for no in nos:
        it = BY_NO[no]
        body = [x for x in it[kind] if not is_chap_tail(x)]
        if not body:
            continue
        out.append("**%s %s**" % (no, it["raw"]))
        out.append("")
        prev = None
        n = 0
        for x in body:
            # 列表项与表格行必须紧凑，否则 markdown 表格/列表会被空行拆散
            compact = x.startswith("-") or x.startswith("|")
            if prev and not compact:
                out.append("")
            if prefix and not x.startswith("|"):
                n += 1
                out.append("- `%s-%s%d` %s" % (no, prefix, n, x.lstrip("- ").strip()))
            else:
                out.append(x)
            if not compact:
                out.append("")
            prev = compact
        out.append("")
    return "\n".join(out).rstrip() + "\n\n"

# 每页「本章核心知识点」清单覆盖的条目（中值定理页额外收编 3.5、3.6）
SUMMARY_MAP = dict(MAP)
SUMMARY_MAP["中值定理"] = ["3.1","3.2","3.3","3.5","3.6"]

def render_summary(nos):
    """章级核心知识点清单：每节一行，含定位与核心判断"""
    out = ["## 本章核心知识点", "", "| 节 | 知识点 | 定位 | 核心判断 |", "|---|---|---|---|"]
    for no in nos:
        it = BY_NO[no]
        name, tag = split_name(it["raw"])
        cl = CLAIMS.get(no, [])
        core = cl[0]["s"] if cl else ""
        out.append("| %s | %s | %s | %s |" % (no, name, tag, core))
    return "\n".join(out) + "\n\n"


def render_chap_tail(nos):
    """章末总结单列，不进知识点编号（数据层已分离）"""
    rows = []
    for no in nos:
        rows.extend(x.strip() for x in BY_NO[no].get("章末小结", []))
    if not rows:
        return ""
    out = ["## 章末小结（原文，不编号）", ""]
    prev = None
    for x in rows:
        compact = x.startswith("-") or x.startswith("|")
        if prev and not compact:
            out.append("")
        out.append(x)
        if not compact:
            out.append("")
        prev = compact
    return "\n".join(out).rstrip() + "\n\n"

TPL = """---
type: concept
name: {name}
aliases: [{aliases}]
updated: 2026-11-08
---

# {name}

> {tagline}

{summary}{core_defs}## 是什么

{what}

## 怎样理解 · 为什么

{why}

{raw_why}## 有什么性质

| 性质 | 说明 |
|---|---|
{nature_table}

{props}{usage}{chap_tail}## 怎么用

{how}

{extra}## 关系

{rel}

## 常见误区

{mistakes}

## 出处

- [[2026-11-06-同济版高数知识点梳理]] —— 提供了{src}
- 原文：`raw/docs/personal-assets/数学/同济版高数知识点梳理.md`
"""

n = 0
for name, d in data.items():
    nature = "\n".join("| %s | %s |" % (a, b) for a, b in d["nature"])
    how = "\n".join("%d. %s" % (i+1, x) for i, x in enumerate(d["how"]))
    rel = "\n".join("- " + x for x in d["rel"])
    mis = "\n".join("- ❌ %s\n  ✅ %s" % (a, b) for a, b in d["mistakes"])
    nos = MAP.get(name, [])
    summary = render_summary(SUMMARY_MAP.get(name, [])) if name in SUMMARY_MAP else ""
    core_defs = render_block(nos, "定义", "## 核心定义与公式") if nos else ""
    raw_why = render_block(nos, "为什么", "## 原文讲解 · 为什么（完整保留）") if nos else ""
    props = render_block(nos, "性质", "## 定理与运算律", "P") if nos else ""
    usage = render_block(nos, "用处", "## 题型与场景", "U") if nos else ""
    s = TPL.format(
        name=name,
        aliases=", ".join(d["aliases"]),
        tagline=d["tagline"],
        summary=summary,
        core_defs=core_defs,
        what=d["what"],
        why=d["why"],
        raw_why=raw_why,
        nature_table=nature,
        props=props,
        usage=usage,
        chap_tail=render_chap_tail(SUMMARY_MAP.get(name, [])) if name in SUMMARY_MAP else "",
        how=how,
        extra=d.get("extra", ""),
        rel=rel,
        mistakes=mis,
        src=d["src"],
    )
    p = os.path.join(OUT_DIR, name + ".md")
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    n += 1
    print("OK  %-16s %3d 行  %5d 字节" % (name, s.count("\n") + 1, len(s.encode("utf-8"))))

print("\n共生成 %d 个概念页" % n)
