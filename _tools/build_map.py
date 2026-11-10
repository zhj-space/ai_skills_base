import re
from pathlib import Path

VAULT = Path("D:/workspace/ai_kb_base/second-brain")
C = VAULT / "wiki" / "概念"
D = VAULT / "wiki" / "文档"
T = "2026-11-06"

# (显示名, 一句话定义 <=20字)
GROUPS = {
 "架构与建模": [
   ("数据仓库", "面向主题、反映历史变化的数据集合"),
   ("数仓分层", "ODS / CDM / ADS 三层加工"),
   ("维度建模", "度量成事实、上下文成维度"),
   ("数据建模四步", "业务→领域→逻辑→物理"),
   ("事实表", "存度量与外键，一行一个事件"),
   ("维度表", "存度量所处的上下文，是分析入口"),
   ("粒度", "事实表一行所表示的细节层次"),
   ("星型模型与雪花模型", "维度直连事实是星型"),
   ("业务过程", "不可拆分的业务行为事件"),
 ],
 "规划与规范": [
   ("总线矩阵", "业务过程 × 维度的规划矩阵"),
   ("一致性维度", "多集市共用、同名同粒度同口径"),
   ("数据域", "自下而上按数据视角划分"),
   ("主题域", "自上而下按分析视角划分"),
   ("数据集市", "面向场景、由公共层供数"),
 ],
 "湖仓与平台": [
   ("数据湖", "原始形式集中存储，先存后定义"),
   ("湖仓一体", "湖上建仓，兼顾灵活与口径"),
   ("数据中台", "把技术复用性转成业务复用性"),
   ("元数据", "描述数据的数据：结构来源口径"),
   ("数据架构演进", "逐代补短板：BI→流式→流批一体"),
 ],
}

L = ["---", "type: theme-map", f"updated: {T}", "---", "", "# topic-map", "",
     "> 按主题导航。找具体概念先看这里定方向；要全量清单去看根目录的 `index.md`。",
     "> **本页只收录概念页，不收录文档页。**", ""]

master = set(f.stem for f in C.glob("*.md"))
used = set()
for g, items in GROUPS.items():
    L += [f"## {g}", ""]
    for name, s in items:
        if name in master:
            L.append(f"- [[{name}]] — {s}")
            used.add(name)
        else:
            L.append(f"- {name} — {s}（待建）")
    L += [""]

rest = master - used
if rest:
    L += ["## 待归类", ""]
    for n in sorted(rest):
        L.append(f"- [[{n}]] — 待补一句话定义")
    L += [""]

L += ["## 其他主题", "",
      "### 技术科学", "",
      f"> 库里可读正文的笔记里，这一域尚未编译（java / python / android 等）。sources 里已有原文，等编译。", "",
      "（待建）", "",
      "### 基础科学", "", "> 数学、操作系统、算法等，sources 里已有原文，等编译。", "", "（待建）", "",
      "### 工具与应用", "", "> 平台操作类（dataworks / sqoop / 运维），等编译。", "", "（待建）", "",
      "---", "", "## 维护规则", "",
      "1. 只在**新建概念页**时改本页；检索时不改",
      "2. 一条 = 概念页链接 + 一句不超过 20 字的定义，写「是什么」不写「讲了什么」",
      "3. 文档页不进本页",
      "4. 同一分组超过 15 条，拆新分组",
      "5. 空主题保留标题写「（待建）」，不要删", ""]
(VAULT / "wiki" / "topic-map.md").write_text("\n".join(L), encoding="utf-8")

# 索引
docs = sorted(D.glob("*.md"))
cpts = sorted(C.glob("*.md"))
I = ["# 知识库索引", "",
     "> 全量状态：`raw/` **305 篇**（正文可读 72 / 读不出 233）。",
     f"> 已编译：**{len(docs)} 篇文档页** + **{len(cpts)} 张概念页** + 1 张topic-map。",
     "> 找方向去 [[topic-map]]；找具体某篇来这里。", "",
     f"## 概念页（{len(cpts)}）", ""]
for f in cpts:
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^> (.+)$", t, re.M)
    I.append(f"- [[{f.stem}]] — {m.group(1) if m else ''}")
I += ["", f"## 文档页（{len(docs)}）", ""]
for f in docs:
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^## 摘要\n\n(.+)$", t, re.M)
    summ = (m.group(1) if m else "")[:56]
    I.append(f"- [[{f.stem}|{f.stem[11:]}]] — {summ}")
I += ["", "---", "", "## 尚未编译", "",
      "- `raw/docs/` 里另有 **62 篇正文可读**但未编译的笔记：spark / kafka / yarn / hive / mr / sqoop / java / 数据库等",
      "- **233 篇 `.note` 专有格式**，API 读不出正文，只保留标题与路径",
      "- 不生成空壳页：读不出的笔记不建 wiki 页，只在 `raw/` 留存", ""]
(VAULT / "index.md").write_text("\n".join(I), encoding="utf-8")

print(f"✓ topic-map：{len(used)} 张已挂载，{len(rest)} 张待归类")
print(f"✓ index.md：{len(docs)} 文档页 + {len(cpts)} 概念页")
