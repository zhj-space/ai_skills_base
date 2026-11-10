#!/usr/bin/env python3
"""大数据组件概念页"""
from pathlib import Path
VAULT = Path("D:/workspace/ai_kb_base/second-brain"); C = VAULT / "wiki" / "概念"; T = "2026-11-06"

P = [
dict(name="Hive", alias=["HiveSQL"], short="把 SQL 翻译成分布式计算任务的引擎",
 defi="构建在 Hadoop 之上的数据仓库工具，把类 SQL 语句翻译成 MapReduce 或 Spark 任务执行。",
 what="Hive 本身不存数据，数据在 HDFS 上，它维护的是「表 → HDFS 目录 + 元数据」的映射。执行引擎可切换：hive on mr 走 MapReduce，hive on spark 走 Spark，后者通常快一个量级。",
 why="它解决的是「让会写 SQL 的人用上分布式算力」这个问题。代价是没有事务、延迟高，适合批处理不适合点查。",
 props=[("不存数据只存元数据", "数据在 HDFS，Hive 管表结构与分区"),
        ("引擎可切换", "on mr / on spark，参数完全不同"),
        ("批处理定位", "一条 SQL 起动辄几十秒到分钟级"),
        ("分区是核心优化手段", "按天分区是最常见的物理组织方式"),
        ("边界", "不适合高并发点查与事务更新，那是 OLAP 数据库的领域")],
 how=["建表时指定存储格式（PARQUET 优于文本）", "按时间或业务维度分区", "按数据量与引擎调 map 内存、并行度、小表 join 阈值", "动态分区要同时开开关并设 nonstrict"],
 rel={"上位": [], "相关": ["MapReduce", "Spark", "HDFS", "Sqoop"], "产出": []},
 pit=[("把 Hive 当 MySQL 用", "没有索引与事务，点查性能极差"),
      ("小文件太多不合并", "每个文件一个 task，启动开销吃掉全部收益")],
 src=["2026-11-06-hive日常维护-锁与回收站", "2026-11-06-hive调优-引擎切换与参数", "2026-11-06-hive数据存储格式"]),

dict(name="MapReduce", alias=["MR"], short="分而治之的批处理计算模型",
 defi="Hadoop 的批处理计算模型：输入切片后并行 map，再按 key 分组 shuffle，最后 reduce 汇总。",
 what="v1 用 JobTracker + TaskTracker，v2 把资源管理拆给 YARN，计算框架只负责 map/reduce 逻辑本身。切片大小默认 128M，决定 map 任务数。",
 why="它把「大数据集计算」抽象成两个函数：map 做转换，reduce 做聚合。框架负责调度、容错、数据本地化。",
 props=[("切片决定并行度", "一个 split 一个 maptask"),
        ("shuffle 是性能瓶颈", "按 key 重分区涉及磁盘与网络"),
        ("v1 有单点与槽位浪费", "这两点直接催生了 YARN"),
        ("数据本地化优先", "map 尽量调度到数据所在节点"),
        ("边界", "迭代计算与低延迟场景不适合，那是 Spark 的地盘")],
 how=["确认输入可切分（压缩格式影响切分）", "控制 map 数与切片大小匹配", "减少 shuffle 数据量", "必要时用 combiner 预聚合"],
 rel={"上位": [], "相关": ["YARN", "HDFS", "Spark", "Hive"], "产出": []},
 pit=[("map 数开太多", "每个 task 有启动开销，小文件场景尤其明显"),
      ("reduce 端数据倾斜不处理", "少数 key 拖慢整个作业")],
 src=["2026-11-06-mr计算模型-v1到v2的架构演进", "2026-11-06-HDFS原理-block与packet"]),

dict(name="Spark", alias=["Apache Spark"], short="基于内存的分布式计算引擎",
 defi="以 RDD 为核心数据结构的分布式计算引擎，主打内存计算与统一批流处理。",
 what="系统架构五部分：Application（用户程序）、Driver（跑 main、建 SparkContext）、Executor（跑 Task、缓存数据）、Cluster Manager（YARN 等）、Operation（Transformation 与 Action）。",
 why="相比 MapReduce，它把中间结果放内存而不是落盘，迭代计算快一个量级。同时一套 API 覆盖批、流、SQL、ML。",
 props=[("RDD 是核心抽象", "一切操作都基于 RDD"),
        ("惰性求值", "Transformation 不触发计算，Action 才触发"),
        ("宽依赖切 Stage", "宽依赖意味着 shuffle"),
        ("可持久化", "多次使用的 RDD 要 cache 或 checkpoint"),
        ("边界", "超大数据集单批处理不如 MR 稳，内存不足会退化")],
 how=["优先 reduceByKey 而非 groupByKey", "多次复用的 RDD 做持久化", "提高并行度到核数的 2-3 倍", "广播小表避免 shuffle join"],
 rel={"上位": [], "组成": ["RDD", "窄依赖与宽依赖"], "相关": ["MapReduce", "YARN", "Hive"], "产出": []},
 pit=[("滥用 groupByKey", "全量 shuffle，能用 reduceByKey 就别用它"),
      ("把所有 RDD 都 cache", "内存被吃满反而触发频繁 GC")],
 src=["2026-11-06-spark计算模型-RDD与依赖", "2026-11-06-spark调优的十一个方向"]),

dict(name="YARN", alias=["Yet Another Resource Negotiator"], short="Hadoop 的资源调度层",
 defi="Hadoop2 引入的资源管理与调度框架，把计算与资源管理解耦，让多种计算框架共用同一集群。",
 what="四件套：ResourceManager 管全局资源、ApplicationMaster 管单个应用、NodeManager 管单节点、Container 是资源单位。调度器有 FIFO、Fair、Capacity 三种。",
 why="在它之前，MapReduce 既管计算又管资源，导致只能跑 MR 一种框架。拆开之后 Spark、Flink、Storm 都能跑同一集群。",
 props=[("资源与计算解耦", "框架只管算，资源交给 YARN"),
        ("每应用一个 AM", "AM 挂了应用就失败，需要重试机制"),
        ("Container 是资源单位", "封装 CPU、内存等，替代 v1 的 slot"),
        ("三种调度器", "FIFO 简单、Fair 公平、Capacity 按队列配额"),
        ("边界", "容器化与云原生场景下，K8s 正在替代它")],
 how=["按业务划分队列并设配额", "给 AM 与 Container 分别留资源", "监控 AM 失败率判断集群健康", "按作业类型选调度器"],
 rel={"上位": [], "组成": ["Container"], "相关": ["MapReduce", "Spark", "HDFS"], "产出": []},
 pit=[("队列配额拍脑袋定", "配额不合理会导致大作业永远排队"),
      ("AM 内存给太小", "AM 一挂整个应用重跑")],
 src=["2026-11-06-yarn架构与资源调度", "2026-11-06-hadoop集群启动流程"]),

dict(name="HDFS", alias=["Hadoop Distributed File System"], short="按块存储的分布式文件系统",
 defi="源自 Google GFS 论文的分布式文件系统，把文件切成 block 分散存储在多个 DataNode 上。",
 what="数据组织分三层：文件切成 block 持久化存储；通信时 block 拆成 packet；packet 内含多个 chunk，每个 chunk 带 checksum。Block 大小由配置决定，默认 128M。",
 why="它是所有 Hadoop 生态组件的存储底座。三层结构的分工是：block 管持久化、packet 管传输、chunk 管校验。",
 props=[("按块存储", "block 是持久化单位，也是容错单位"),
        ("多副本", "默认 3 副本，靠复制保证可靠"),
        ("适合大文件", "大量小文件会压垮 NameNode 元数据"),
        ("一次写入多次读", "不适合频繁修改"),
        ("边界", "低延迟随机读写不适合，那是数据库或对象存储的场景")],
 how=["控制单文件大小，避免大量小文件", "按访问频率设副本数", "定期合并小文件", "NameNode 做高可用"],
 rel={"上位": [], "相关": ["MapReduce", "YARN", "Hive", "Spark"], "产出": []},
 pit=[("把 HDFS 当普通文件系统用", "随机写与频繁改名的性能极差"),
      ("小文件不做合并", "NameNode 内存被元数据吃光")],
 src=["2026-11-06-HDFS原理-block与packet", "2026-11-06-hadoop集群启动流程"]),

dict(name="Container", alias=["容器资源单位"], short="YARN 的资源抽象，封装 CPU 与内存",
 defi="YARN 中的抽象资源容器，封装一定量的 CPU、内存、IO 等资源，是运行 map/reduce task 的资源单位。",
 what="它替代了 Hadoop v1 的 slot 概念。v1 的 map 槽和 reduce 槽是事先固定的，只用其中一种就浪费一半；Container 按实际需求分配，资源维度更合理。",
 why="一个 split 对应一个 maptask、一个 container、一个 yarnchild 进程——这条链是理解 YARN 资源分配的最小模型。",
 props=[("资源维度而非槽位", "按需分配 CPU 与内存"),
        ("与进程一一对应", "一个 container 跑一个 task 进程"),
        ("由 NodeManager 提供", "AM 向 RM 申请，RM 指挥 NM 开启"),
        ("边界", "container 不是 Docker 容器，是 YARN 自己的资源抽象")],
 how=["按 task 实际内存需求设 container 大小", "避免 container 远大于实际使用", "监控 container 等待时间判断资源是否不足"],
 rel={"上位": ["YARN"], "相关": ["MapReduce", "Spark"]},
 pit=[("把 YARN container 当成 Docker", "两者是不同层次的概念，容易在面试里答错")],
 src=["2026-11-06-yarn架构与资源调度", "2026-11-06-mr计算模型-v1到v2的架构演进"]),

dict(name="RDD", alias=["弹性分布式数据集", "Resilient Distributed Dataset"], short="Spark 的核心数据抽象",
 defi="Spark 底层的分布式数据集抽象，逻辑分区、不可变、可重算。",
 what="五个特性：一组分区（逻辑分区，存元数据计算信息而非真实数据）、每个分片一个计算函数、依赖关系、可选分区策略、可选最优位置。",
 why="不可变 + 记录依赖 = 免费容错。某个分区丢了，按依赖链重算那一段就行，不用重跑整个作业。",
 props=[("不可变", "每次转换生成新 RDD，形成依赖链"),
        ("逻辑分区", "分区不存真实数据，存的是计算描述"),
        ("可重算", "丢分区按血缘重算，这是容错机制"),
        ("惰性", "Transformation 只记录，Action 才执行"),
        ("边界", "数据量大到内存放不下时会落盘，性能优势削弱")],
 how=["多次复用的 RDD 做 cache 或 checkpoint", "分区数调到核数 2-3 倍", "key-value 形式才用自定义 Partitioner"],
 rel={"上位": ["Spark"], "组成": ["窄依赖与宽依赖"], "相关": ["MapReduce"]},
 pit=[("以为 RDD 存了数据", "它存的是分区与计算描述，数据在执行时才产生")],
 src=["2026-11-06-spark计算模型-RDD与依赖", "2026-11-06-spark调优的十一个方向"]),

dict(name="窄依赖与宽依赖", alias=["Narrow Dependency", "Wide Dependency", "Shuffle"], short="决定 Spark 是否切 Stage",
 defi="RDD 之间依赖的两种形态：窄依赖是父分区最多被子 RDD 一个分区使用，宽依赖是子分区依赖父 RDD 的所有分区。",
 what="窄依赖（1 对 1、n 对 1）可以流水线执行，父子分区在同一节点流水处理。宽依赖（1 对 n、n 对 n）意味着 shuffle，是划分 Stage 的边界。典型宽依赖操作：groupByKey、sortByKey。",
 why="窄依赖便宜，宽依赖昂贵。所以优化 Spark 作业的核心就是「尽量把宽依赖变成窄依赖」，比如用 reduceByKey 代替 groupByKey、用 broadcast join 代替 shuffle join。",
 props=[("宽依赖 = shuffle", "涉及磁盘与网络传输"),
        ("宽依赖切 Stage", "Stage 内部才能流水线"),
        ("依赖支撑容错", "丢分区按依赖链重算，不用全量重跑"),
        ("Shuffle 有两种 Manager", "Hash 与 Sort"),
        ("边界", "join 的依赖类型取决于是否分区对齐，不是固定的")],
 how=["能 reduceByKey 就不 groupByKey", "小表广播避免 shuffle", "调整分区数减少 shuffle 数据倾斜", "必要时预分区（partitionBy）让后续 join 变窄依赖"],
 rel={"上位": ["RDD"], "相关": ["Spark", "MapReduce"]},
 pit=[("把所有 join 都当窄依赖", "只有分区对齐的 join 才是窄依赖，否则要 shuffle")],
 src=["2026-11-06-spark计算模型-RDD与依赖"]),

dict(name="Sqoop", alias=["sqoop"], short="关系库与 Hadoop 之间的批量搬运工具",
 defi="在关系型数据库与 Hadoop/Hive 之间做批量数据导入导出的工具，本质是生成 MapReduce 作业。",
 what="import 从关系库导到 HDFS/Hive，export 从 HDFS 导回关系库。实践中最大的麻烦不是命令本身，而是列名对齐与连接稳定性。",
 why="批量同步场景下它比写 JDBC 程序稳，因为它自带分片、类型映射与失败重试。但它是批处理，不适合实时同步。",
 props=[("import / export 两个方向", "关系库 ↔ HDFS"),
        ("列名要对齐", "常先用 Hive 查表头再拼 select 语句"),
        ("连接串要加稳定性参数", "keepAlive、maxReconnects、批量大小"),
        ("边界", "增量与实时同步不适合，那是 CDC 工具的领域")],
 how=["先用 Hive 查出目标表表头，拼成 select 列清单", "连接串加 defaultRowFetchSize 控制批量", "加 tcpKeepAlive 与 maxReconnects 防断连", "导出用 reWriteBatchedInserts 提升批量插入性能"],
 rel={"上位": [], "相关": ["Hive", "HDFS", "MapReduce"]},
 pit=[("select * 直接导", "源表加字段后列错位，数据静默错乱"),
      ("密码明文写在脚本里", "应走环境变量或凭证管理，脚本不要进版本库")],
 src=["2026-11-06-sqoop导入-hive表头自动拼接", "2026-11-06-sqoop导出到pgsql"]),

dict(name="Kafka", alias=["消息队列"], short="高吞吐分布式消息队列",
 defi="分布式发布订阅消息系统，以极高吞吐量著称，常用于日志采集与流式数据管道。",
 what="高吞吐来自两个设计：写侧走操作系统页缓存加磁盘顺序追加；读侧用零拷贝，跳过内核缓存到应用缓存、再回 Socket 缓存的两次拷贝。消息传递语义分最多一次、至少一次、精确一次三档。",
 why="它把「写磁盘」这件事做得跟写内存差不多快，所以能用便宜的磁盘扛住每秒几十万条。",
 props=[("写走页缓存 + 顺序写", "顺序写性能接近写内存"),
        ("读走零拷贝", "省掉两次内存拷贝与上下文切换"),
        ("消息语义三档", "业务要求不同选档不同，精确一次代价最高"),
        ("分区是并行单位", "分区数决定消费并行度"),
        ("边界", "不适合超长消息与复杂路由，那是其他 MQ 的强项")],
 how=["按消费并行度设分区数", "生产端配 acks 权衡可靠与延迟", "消费端做好幂等，避免至少一次语义下的重复", "监控消费延迟而非只看堆积量"],
 rel={"上位": [], "组成": ["零拷贝", "页缓存与顺序写"], "相关": ["Spark", "Hive"]},
 pit=[("要精确一次却不做幂等", "语义靠消费端配合，光配生产端不够")],
 src=["2026-11-06-kafka原理-高吞吐与消息语义"]),

dict(name="零拷贝", alias=["Zero Copy"], short="跳过两次内存拷贝的传输技术",
 defi="一种数据传输优化：让数据从内核缓存直接发到网卡，跳过「内核→应用→Socket」的两次拷贝。",
 what="常规读发送流程：磁盘 → 内核页缓存 → 应用缓存 → Socket 缓存 → 网卡。零拷贝把中间两步省掉，Socket 缓存里只放数据描述符，数据本身仍在页缓存。",
 why="省的不只是两次内存拷贝，还有随之而来的上下文切换。这是 Kafka 能高吞吐消费的关键之一。",
 props=[("省两次拷贝", "内核缓存直接到网卡"),
        ("省上下文切换", "用户态与内核态少切两次"),
        ("有前提", "数据不需要在应用层加工"),
        ("边界", "需要对数据做转换时就享受不到，比如加密或格式转换")],
 how=["确认传输链路无需应用层改数据", "用 sendfile 类接口而非 read+write", "监控是否真的零拷贝（抓包看内存拷贝次数）"],
 rel={"上位": ["Kafka"], "相关": ["页缓存与顺序写"]},
 pit=[("以为零拷贝等于不拷贝", "它省的是内存拷贝，数据仍要过一次 DMA")],
 src=["2026-11-06-kafka原理-高吞吐与消息语义"]),

dict(name="页缓存与顺序写", alias=["page cache", "磁盘顺序写"], short="Kafka 高吞吐的写侧基础",
 defi="利用操作系统的页缓存承接写入，配合文件末尾追加的方式，把写磁盘的性能拉到接近写内存。",
 what="写文件时先写进 OS 的 page cache（本质是内存），由操作系统决定何时刷盘。同时采用磁盘顺序追加而非随机位置修改。",
 why="机械磁盘随机写极慢，但顺序写可以接近内存速度。两者叠加，Kafka 用普通磁盘实现了极高写入吞吐。",
 props=[("写内存不是写磁盘", "page cache 由 OS 管理"),
        ("顺序追加", "只在文件末尾写，不找位置"),
        ("刷盘时机由 OS 决定", "断电可能丢少量未刷数据，可靠性靠副本补"),
        ("边界", "页缓存被其他进程挤占时性能会掉，需要预留内存")],
 how=["给 Kafka 预留足够页缓存", "避免与其他内存密集服务混部", "副本数补足断电丢数据的风险"],
 rel={"上位": ["Kafka"], "相关": ["零拷贝"]},
 pit=[("用随机写的方式存消息", "顺序写才是性能来源，改成分片随机写立刻变慢")],
 src=["2026-11-06-kafka原理-高吞吐与消息语义"]),

dict(name="Iceberg", alias=["Apache Iceberg"], short="数据湖上的表存储格式",
 defi="一种面向数据湖的表存储格式，为湖上的数据提供事务、Schema 演进与多引擎兼容能力。",
 what="底层用 avro 与 parquet 存数据，向上兼容 flink、spark 等计算引擎和 hive、presto、ck 等 OLAP 引擎，以轻量级 jar 包方式集成。它是「流批一体」在数据湖场景的落地方案之一。",
 why="数据湖的问题是「一堆文件，没有表的概念」——没有事务、没法改 Schema、多引擎读到的结果可能不一致。Iceberg 补的就是这一层。",
 props=[("是表格式不是存储引擎", "数据仍在 HDFS/对象存储上"),
        ("支持 Schema 演进", "加列删列不影响历史数据"),
        ("多引擎兼容", "同一份数据多种引擎都能读"),
        ("边界", "装了 Iceberg 不等于湖仓一体，还缺建模与治理")],
 how=["选一个表格式作为底座（Iceberg/Hudi/Delta）", "原始数据以表形式入湖，带 Schema 与版本", "在湖上建模型层与指标层", "探索分析直读原始表，规范报表走模型层"],
 rel={"上位": [], "相关": ["数据湖", "湖仓一体", "Spark"]},
 pit=[("以为 Iceberg 能替代数仓", "它只管表格式，不管建模与口径")],
 src=["2026-11-06-iceberg初步总结"]),
]

def render(d):
    L = ["---", "type: concept", f"name: {d['name']}",
         f"aliases: [{', '.join(d['alias'])}]" if d['alias'] else "aliases: []", f"updated: {T}", "---", "", f"# {d['name']}", "",
         f"> {d['defi']}", "", "## 是什么", "", d["what"], "",
         "## 怎样理解 · 为什么", "", d["why"], "",
         "## 有什么性质", "", "| 性质 | 说明 |", "|---|---|"]
    for k, v in d["props"]:
        L.append(f"| {'**' + k + '**' if k == '边界' else k} | {v} |")
    L += ["", "## 怎么用", ""]
    for i, s in enumerate(d["how"], 1):
        L.append(f"{i}. {s}")
    L += ["", "## 关系", ""]
    for k in ["上位", "组成", "相关", "产出"]:
        arr = d["rel"].get(k) or []
        if arr: L.append(f"- {k}：" + " · ".join(f"[[{x}]]" for x in arr))
    L += ["", "## 常见误区", ""]
    for bad, good in d["pit"]:
        L.append(f"- ❌ {bad}"); L.append(f"  ✅ {good}")
    L += ["", "## 出处", ""]
    for s in d["src"]: L.append(f"- [[{s}]]")
    L += [""]
    return "\n".join(L)

for d in P:
    (C / f"{d['name']}.md").write_text(render(d), encoding="utf-8")
print(f"✓ 概念页 {len(P)} 张（大数据组件）")
for d in P: print(f"    {d['name']}")
