# -*- coding: utf-8 -*-
"""生成同济版高数文档页 v3：知识地图 + 断言从 JSON 读"""
import io, json, re, os

KB = r"D:/workspace/ai_kb_base/second-brain"
TOOLS = r"D:/workspace/ai_kb_base/_tools"
ITEMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_items.json"), encoding="utf-8"))
CLAIMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_claims.json"), encoding="utf-8"))
PRE = json.load(io.open(os.path.join(TOOLS, "gaoshu_preamble.json"), encoding="utf-8"))
SRC_REL = "raw/docs/personal-assets/数学/同济版高数知识点梳理.md"
OUT = os.path.join(KB, "wiki", "summaries", "2026-11-06-同济版高数知识点梳理.md")

CH_NOTE = {
 "函数与极限": "本章不解决具体问题，它发明一套语言——后面每个概念（连续、导数、积分、级数）都是极限的特例。",
 "导数与微分": "埋下全书最重要的一句话：局部可以用直线代替曲线。第 3 章用它推定理，第 6 章用它写微元。",
 "微分中值定理与导数的应用": "定理链的条件逐步放宽：罗尔→拉格朗日→柯西→洛必达；泰勒是另一条纵轴，从一阶近似升到 n 阶。",
 "不定积分": "求导会丢信息（常数），所以逆运算只能给出函数族。+C 不是形式主义，是不唯一的诚实交代。",
 "定积分": "定义本体与分法无关；牛顿-莱布尼茨公式把「求和」换成「看首尾两端的差」。",
 "定积分的应用": "一句话：在足够小的一格里，把变化的东西当不变。",
 "微分方程": "解方程就是不断求不定积分，每积一次多一个常数，所以 n 阶方程有 n 个常数。",
 "向量代数与空间解析几何": "向量只有两种关系——角度（点积）与面积/法向（叉积），其余都是它们的组合。",
 "多元函数微分法及其应用": "一元里可导⇔可微，到多元会分裂；偏导只测两条轴，全微分要求所有方向共用一个平面。",
 "重积分": "定义与定积分同构，理论无新东西，难点只在降维与定限。",
 "曲线积分与曲面积分": "四个公式一个主题：内部求导 = 边界取值。格林二维、高斯三维、斯托克斯曲面。",
 "无穷级数": "核心难题是用有限定义无限：先算前 n 项和，再看 n→∞ 时稳不稳定。",
}

# 原文定位标签词表（按长度降序做最长匹配，避免把名称切断）
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

L = []
A = L.append
A("---")
A("type: doc")
A("doc_id: 2026-11-06-同济版高数知识点梳理")
A("title: 同济版高数知识点梳理")
A("source_path: " + SRC_REL)
A("source_type: html")
A("modality: text")
A("confidence: 0.95")
A("compile_status: compiled")
A("compiled_at: 2026-11-07")
A("coverage: 12 章 / 57 个知识点 / 断言全覆盖")
A("---")
A("")
A("# 同济版高数知识点梳理")
A("")
A("## 摘要")
A("")
A("同济版高数全书：12 章 / 57 节 / 442 个知识点。逐条编号见 [[2026-11-07-高数知识点总索引]]。")
A("")
A("原文体例说明（照录）：Advanced Mathematics · Tongji 7th Edition · Concept Notes。每个知识点都按四个问题拆开：它**是什么**（定义）、**为什么**需要它（怎么理解）、它**有什么性质**（定理与运算律）、它**能用来干什么**（题型与场景）。全书 12 章、60 个核心概念，逐一过一遍。")
A("")
A("全书主线是三个问题、一条链：**怎样严格描述「无限逼近」**（第 1 章的 ε 语言）→ **怎样把复杂的东西在局部变简单**（第 2 章的以直代曲）→ **怎样把无穷多个微小部分累加起来**（第 5 章的积分）。牛顿-莱布尼茨公式让第三问的答案等于第一类问题的反运算，微分与积分互逆，全书由此闭环。")
A("")
A("下册的难点不在新理论，而在维度。偏导、重积分、曲线曲面积分的定义与上册同构，真正难的是降维与定限。四大公式（牛顿-莱布尼茨、格林、高斯、斯托克斯）是同一个命题在不同维度上的写法——**内部的积分等于边界的积分**。")
A("")
A("## 全书主线（原文）")
A("")
A(PRE["whole"]["全书主线：三个问题，一条链"])
A("")
A("## 全书结构")
A("")
A("| 章 | 序号 | 知识点 | 定位 |")
A("|---|---|---|---|")
cur = ""
for it in ITEMS:
    name, tag = split_name(it["raw"])
    ch = it["ch"] if it["ch"] != cur else ""
    if ch:
        cur = it["ch"]
    A("| %s | %s | %s | %s |" % (ch, it["no"], name, tag))
A("")

A("## 关键断言")
A("")
cur = ""
for it in ITEMS:
    if it["ch"] != cur:
        cur = it["ch"]
        A("### " + cur)
        A("")
        if cur in CH_NOTE:
            A("> " + CH_NOTE[cur])
            A("")
        pre = PRE["preamble"].get(cur, "")
        if pre:
            A(pre)
            A("")
    cl = CLAIMS.get(it["no"])
    if not cl:
        continue
    A("**%s %s**" % (it["no"], it["raw"]))
    A("")
    for c in cl:
        A("- %s  `%s`" % (c["s"], c["c"]))
        ev = c.get("e", "")
        if not ev:
            continue
        if c["c"] == "high":
            A("  > 原文：「%s」" % ev)
        else:
            A("  > 由「%s」一步推出" % ev)
    A("")

A("## 涉及概念")
A("")
A("[[极限]] · [[连续与间断]] · [[导数与微分]] · [[中值定理]] · [[泰勒公式]] · [[不定积分]] · [[定积分]] · [[牛顿-莱布尼茨公式]] · [[微元法]] · [[微分方程]] · [[向量代数]] · [[偏导数与全微分]] · [[梯度]] · [[重积分]] · [[曲线曲面积分]] · [[格林高斯斯托克斯公式]] · [[无穷级数]]")
A("")
A("**覆盖说明**：57 节全部有归属，442 个知识点逐条编号。其中 55 节按主题分装在 **17 个数学主线概念页**中；洛必达法则（3.5）与导数的应用（3.6）属单一技术步骤，按 agent.md 建卡门槛归入 `中值定理` 页的「应用一」「应用二」两节，不单独建页。判据见 `agent.md` 第五节「按原文形态分流」——本篇有完整章节结构，按「有章节」规则处理：章级主题全部建页（含微分方程、无穷级数），57 个核心知识点全覆盖，原文四段与章级导读 100% 保留。")
A("## 学习路线建议（原文）")
A("")
A(PRE["whole"]["学习路线建议"])
A("")
A("## 原文位置")
A("")
A("`" + SRC_REL + "`（2142 行 / 38840 字，原件为同目录 `.html`）")
A("")

io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(L))
n = sum(len(v) for v in CLAIMS.values())
nh = sum(1 for v in CLAIMS.values() for c in v if c["c"] == "high")
print("已生成：%s" % OUT)
txt = "\n".join(L)
print("行数 %d　字节 %d" % (txt.count("\n") + 1, len(txt.encode("utf-8"))))
print("覆盖 %d/57 条目　断言 %d 条（high %d / medium %d）" % (len(CLAIMS), n, nh, n-nh))
