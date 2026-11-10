# -*- coding: utf-8 -*-
"""生成高数知识点总索引：57 节 + 203 条性质 + 222 条用处，逐条编号"""
import io, json, os, re
from chap_tail import is_chap_tail

KB = r"D:/workspace/ai_kb_base/second-brain"
TOOLS = r"D:/workspace/ai_kb_base/_tools"
ITEMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_items.json"), encoding="utf-8"))
OUT = os.path.join(KB, "wiki", "summaries", "2026-11-07-高数知识点总索引.md")

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

# 概念页归属（用于交叉引用）
MAP = {
 "极限": ["1.1","1.2","1.3","1.4"], "连续与间断": ["1.5","1.6"],
 "导数与微分": ["2.1","2.2","2.3","2.4"], "中值定理": ["3.1","3.2","3.3","3.5","3.6"],
 "泰勒公式": ["3.4"], "不定积分": ["4.1","4.2","4.3","4.4"],
 "定积分": ["5.1","5.2","5.5"], "牛顿-莱布尼茨公式": ["5.3","5.4"],
 "微元法": ["6.1","6.2","6.3"], "微分方程": ["7.1","7.2","7.3","7.4"],
 "向量代数": ["8.1","8.2","8.3","8.4"], "偏导数与全微分": ["9.1","9.2","9.3","9.4"],
 "梯度": ["9.5","9.6"], "重积分": ["10.1","10.2","10.3","10.4"],
 "曲线曲面积分": ["11.1","11.2","11.5"], "格林高斯斯托克斯公式": ["11.3","11.4","11.6"],
 "无穷级数": ["12.1","12.2","12.3","12.4","12.5"],
}
OWNER = {}
for page, nos in MAP.items():
    for no in nos:
        OWNER[no] = page

def clean(x):
    return x.strip()

L = []
A = L.append
A("---")
A("type: doc")
A("doc_id: 2026-11-07-高数知识点总索引")
A("title: 高数知识点总索引")
A("source_path: raw/docs/personal-assets/数学/同济版高数知识点梳理.md")
A("source_type: html")
A("modality: text")
A("confidence: 0.95")
A("compile_status: compiled")
A("compiled_at: 2026-11-07")
A("coverage: 12 章 / 57 节 / 442 个知识点逐条编号")
A("---")
A("")
A("---")
A("")
A("# 高数知识点总索引")
A("")
A("> 把原文拆到最小颗粒：57 节 → 57 条定义 + 203 条性质 + 191 条用法 = **442 个知识点**，逐条编号，可按编号检索。另将每章末尾的 29 条串联小结单列，不计入知识点。")
A("")
A("编号规则：`节号-D` 定义 · `节号-P<n>` 性质 · `节号-U<n>` 用处。例：`3.2-P3` = 拉格朗日定理的第 3 条性质。")
A("")

# 统计表
A("## 分布")
A("")
A("| 章 | 节数 | 定义 | 性质 | 用处 | 小计 |")
A("|---|---|---|---|---|---|")
chap_order = []
for it in ITEMS:
    if it["ch"] not in chap_order:
        chap_order.append(it["ch"])
grand = [0, 0, 0]
for ch in chap_order:
    sub = [x for x in ITEMS if x["ch"] == ch]
    d = sum(1 for x in sub for _ in x["定义"])
    p = sum(len(x["性质"]) for x in sub)
    u = sum(len(x["用处"]) for x in sub)
    # 定义按条目算 1 条（一个条目一个定义）
    dd = len(sub)
    grand[0] += dd; grand[1] += p; grand[2] += u
    A("| %s | %d | %d | %d | %d | %d |" % (ch, len(sub), dd, p, u, dd+p+u))
A("| **合计** | **57** | **%d** | **%d** | **%d** | **%d** |" % (grand[0], grand[1], grand[2], sum(grand)))
A("")

# 逐章逐节
cur_ch = ""
cur_no = ""
for it in ITEMS:
    if it["ch"] != cur_ch:
        cur_ch = it["ch"]
        A("## " + cur_ch)
        A("")
    name, tag = split_name(it["raw"])
    owner = OWNER.get(it["no"], "")
    A("### %s %s" % (it["no"], name))
    A("")
    A("`%s`　归属：[[%s]]" % (tag, owner))
    A("")
    # 定义
    body = [clean(x) for x in it["定义"] if clean(x)]
    if body:
        A("**%s-D 定义**" % it["no"])
        A("")
        prev = None
        for x in body:
            compact = x.startswith("-") or x.startswith("|")
            if prev and not compact:
                A("")
            A(x)
            if not compact:
                A("")
            prev = compact
        A("")
    # 性质
    props = [clean(x) for x in it["性质"] if clean(x) and not is_chap_tail(x)]
    tails = [clean(x) for x in it.get("章末小结", []) if clean(x)]
    if props:
        A("**性质**")
        A("")
        for k, x in enumerate(props, 1):
            A("- `%s-P%d` %s" % (it["no"], k, x.lstrip("- ").strip()))
        A("")
    # 用处
    uses = [clean(x) for x in it["用处"] if clean(x) and not is_chap_tail(x)]
    if uses:
        A("**用处**")
        A("")
        for k, x in enumerate(uses, 1):
            A("- `%s-U%d` %s" % (it["no"], k, x.lstrip("- ").strip()))
        A("")
    if tails:
        A("**章末小结（原文，不编号）**")
        A("")
        for x in tails:
            A(x)
            A("")
    # 标记未归属（不该有）
    if not owner:
        A("> ⚠ 未归属概念页")
        A("")

A("## 出处")
A("")
A("`raw/docs/personal-assets/数学/同济版高数知识点梳理.md`（2143 行 / 38840 字）")
A("")

txt = "\n".join(L)
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
print("已生成：%s" % OUT)
print("行数 %d　字节 %d" % (txt.count("\n")+1, len(txt.encode("utf-8"))))
print("知识点合计：定义 %d + 性质 %d + 用处 %d = %d" % (grand[0], grand[1], grand[2], sum(grand)))
