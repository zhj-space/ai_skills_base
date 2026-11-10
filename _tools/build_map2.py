import re
from pathlib import Path

VAULT = Path("D:/workspace/ai_kb_base/second-brain")
C = VAULT / "wiki" / "概念"
D = VAULT / "wiki" / "文档"
T = "2026-11-06"

THEMES = [
 ("数据科学", "处理数据的建模、治理、计算与平台", [
   ("架构与建模", [("数据仓库","面向主题、反映历史变化的数据集合"),("数仓分层","ODS / CDM / ADS 三层加工"),
     ("维度建模","度量成事实、上下文成维度"),("数据建模四步","业务→领域→逻辑→物理"),
     ("事实表","存度量与外键，一行一个事件"),("维度表","存度量所处的上下文，是分析入口"),
     ("粒度","事实表一行所表示的细节层次"),("业务过程","不可拆分的业务行为事件"),
     ("星型模型与雪花模型","维度直连事实是星型")]),
   ("规划与规范", [("总线矩阵","业务过程 × 维度的规划矩阵"),("一致性维度","多集市共用、同名同粒度同口径"),
     ("数据域","自下而上按数据视角划分"),("主题域","自上而下按分析视角划分"),
     ("数据集市","面向场景、由公共层供数")]),
   ("湖仓与平台", [("数据湖","原始形式集中存储，先存后定义"),("湖仓一体","湖上建仓，兼顾灵活与口径"),
     ("数据中台","把技术复用性转成业务复用性"),("元数据","描述数据的数据：结构来源口径"),
     ("数据架构演进","逐代补短板：BI→流式→流批一体"),("Iceberg","数据湖上的表存储格式")]),
   ("计算引擎与存储", [("Spark","基于内存的分布式计算引擎"),("RDD","Spark 的核心数据抽象"),
     ("窄依赖与宽依赖","决定 Spark 是否切 Stage"),("MapReduce","分而治之的批处理计算模型"),
     ("Hive","把 SQL 翻译成分布式计算任务"),("YARN","Hadoop 的资源调度层"),
     ("Container","YARN 的资源抽象"),("HDFS","按块存储的分布式文件系统"),
     ("Sqoop","关系库与 HDFS 之间的搬运工具"),("Kafka","高吞吐分布式消息队列"),
     ("零拷贝","跳过两次内存拷贝的传输技术"),("页缓存与顺序写","Kafka 高吞吐的写侧基础")]),
 ]),
 ("技术科学", "构建系统的技术知识：语言、运行时、数据库", [
   ("语言与运行时", [("Java","面向对象的托管型编程语言"),("JVM","Java 的运行时，管内存与字节码"),
     ("垃圾回收","自动回收不可达对象")]),
   ("数据库", [("pgsql","功能完备的开源关系库"),("SQLServer","微软的关系型数据库"),
     ("SQL运维","用 SQL 定位问题与优化查询")]),
 ]),
 ("基础科学", "计算机底层原理与思维方法", [
   ("系统与硬件", [("计算机体系结构","CPU、存储与指令系统的组织"),("流水线","拆级并行提升吞吐"),
     ("局部性原理","程序访问的时间与空间聚集"),("操作系统","管理硬件资源与程序运行")]),
   ("数据库理论", [("数据库系统","三级模式与关系代数构成的底层理论"),("关系代数","SQL 背后的形式化查询语言")]),
   ("思维方法", [("思维体系模型","个人思考与学习的公式化框架")]),
 ]),
]

L = ["---", "type: theme-map", f"updated: {T}", "---", "", "# topic-map", "",
     "> 按主题导航。找具体概念先看这里定方向；要全量清单去看根目录的 `index.md`。",
     "> **本页只收录概念页，不收录文档页。**", ""]

have = {f.stem for f in C.glob("*.md")}
used = set()
for theme, desc, groups in THEMES:
    L += [f"## {theme}", "", f"> {desc}", ""]
    for g, items in groups:
        L += [f"### {g}", ""]
        for n, s in items:
            if n in have:
                L.append(f"- [[{n}]] — {s}"); used.add(n)
            else:
                L.append(f"- {n} — {s}（待建）")
        L += [""]

rest = have - used
if rest:
    L += ["## 待归类", ""]
    for n in sorted(rest): L.append(f"- [[{n}]] — 待补一句话定义")
    L += [""]

L += ["## 工具与应用", "", "> 平台操作类笔记（dataworks / 部署 / 编辑器）暂以文档页形式存在，未提炼为概念卡。", "",
      "（待建）", "", "---", "", "## 维护规则", "",
      "1. 只在**新建概念页**时改本页；检索时不改",
      "2. 一条 = 概念页链接 + 一句不超过 20 字的定义",
      "3. 文档页不进本页",
      "4. 同一分组超过 15 条，拆新分组",
      "5. 空主题保留标题写「（待建）」，不要删", ""]
(VAULT / "wiki" / "topic-map.md").write_text("\n".join(L), encoding="utf-8")

# 索引
docs = sorted(D.glob("*.md"))
cpts = sorted(C.glob("*.md"))
normal_docs = [f for f in docs if "凭据已屏蔽" not in f.stem]
withheld = [f for f in docs if "凭据已屏蔽" in f.stem]

I = ["# 知识库索引", "",
     "> 全量状态：`raw/` **305 篇**（正文可读 72 / 读不出 233）。",
     f"> 已编译：**{len(docs)} 篇文档页**（含 {len(withheld)} 篇凭据屏蔽页）+ **{len(cpts)} 张概念页** + 1 张topic-map。",
     "> 找方向去 [[topic-map]]；找具体某篇来这里。", "",
     f"## 概念页（{len(cpts)}）", ""]
for f in cpts:
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^> (.+)$", t, re.M)
    I.append(f"- [[{f.stem}]] — {m.group(1) if m else ''}")
I += ["", f"## 文档页（{len(normal_docs)}）", ""]
for f in normal_docs:
    t = f.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^## 摘要\n\n(.+)$", t, re.M)
    I.append(f"- [[{f.stem}|{f.stem[11:]}]] — {(m.group(1) if m else '')[:50]}")
I += ["", f"## 已屏蔽（{len(withheld)}）", "",
      "> 以下笔记含账号、密钥类凭据，**不进摘要、不进概念网络、不参与检索**。原文仍在 `raw/` 本地，不要粘贴到任何模型对话中。", ""]
for f in withheld:
    I.append(f"- {f.stem[11:]}")
I += ["", "---", "", "## 尚未编译", "",
      "- **233 篇 `.note` 专有格式**，API 读不出正文，只保留标题与路径",
      "- **11 篇空占位笔记**（dataworks 目录下，正文仅标题、无内容），不建页",
      "- 不生成空壳页：上述都不建 wiki 页，只在 `raw/` 留存", ""]
(VAULT / "index.md").write_text("\n".join(I), encoding="utf-8")

print(f"✓ topic-map：{len(used)} 张已挂载，{len(rest)} 张待归类")
print(f"✓ 索引：{len(docs)} 文档页（{len(withheld)} 屏蔽）+ {len(cpts)} 概念页")
