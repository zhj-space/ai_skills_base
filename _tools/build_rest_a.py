#!/usr/bin/env python3
"""编译大数据域文档页"""
import re
from pathlib import Path

VAULT = Path("D:/workspace/ai_kb_base/second-brain")
DOCS = VAULT / "wiki" / "文档"
DOCS.mkdir(parents=True, exist_ok=True)
T = "2026-11-06"

def safe(s):
    return re.sub(r'[\\/:*?"<>|\r\n\t]', "-", s).strip()

# (标题, 源相对路径, 摘要, [(断言,档位,证据)], [概念], 备注)
P = [
("spark计算模型-RDD与依赖",
 "个人资产体系/大数据/Spark/spark计算模型-深入理解spark架构和原理.md",
 "Spark 的系统架构由 Application、Driver、Executor、Cluster Manager、Operation 五部分组成。核心数据结构是 RDD，它有五个特性：分区、每分片一个计算函数、依赖关系、可选分区策略、可选最优位置。窄依赖形成流水线，宽依赖意味着 Shuffle，也是划分 Stage 的依据。",
 [("Spark 应用程序由 Driver 和多个 Executor 组成", "high",
   "应用程序(Application): 基于Spark的用户程序，包含了一个Driver Program 和集群中多个的Executor"),
  ("RDD 的分区数是逻辑分区，存储的是元数据计算信息而非真实数据", "high",
   "分区，逻辑上分区，并非存储真实数据，存储了一些元数据的计算信息"),
  ("宽依赖意味着 Shuffle，是 Spark 划分 Stage 边界的依据", "high",
   "宽依赖意味着Shuffle操作，这是 Spark划分Stage的边界的依据。"),
  ("窄依赖是父 RDD 的每个分区最多被子 RDD 的一个分区使用", "high",
   "窄依赖指的是每一个 parent RDD的 Partition最多被 child rdd的一个 Partition所使用")],
 ["Spark", "RDD", "窄依赖与宽依赖", "MapReduce"], ""),

("kafka原理-高吞吐与消息语义",
 "个人资产体系/大数据/kafka/kafka原理.md",
 "Kafka 的高吞吐来自三个设计：写走操作系统页缓存加磁盘顺序写、读用零拷贝跳过两次内存拷贝。消息传递语义分三档：最多一次、至少一次、精确一次，业务要求不同选档不同。",
 [("Kafka 写数据基于操作系统页缓存，本质是在写内存", "high",
   "Kafka是基于操作系统的页缓存来实现文件写入的"),
  ("磁盘顺序写性能可以接近写内存", "high",
   "如果你是追加文件末尾按照顺序的方式来写数据的话，那么这种磁盘顺序写的性能基本上可以跟随机写内存的性能本身也是差不多的"),
  ("零拷贝去掉了从内核缓存到应用缓存、再回 Socket 缓存的两次拷贝", "high",
   "通过零拷贝技术，就不需要把os cache里的数据拷贝到应用缓存，再从应用缓存拷贝到Socket缓存了"),
  ("消息传递语义分最多一次、至少一次、精确一次三档", "high",
   "分为三种：")],
 ["Kafka", "零拷贝", "页缓存与顺序写"], ""),

("mr计算模型-v1到v2的架构演进",
 "个人资产体系/大数据/MapReduce/mr计算模型-深入理解mr原理.md",
 "Hadoop v1 的 JobTracker 单点、性能瓶颈、TaskTracker 槽位浪费等问题，在 v2 被拆成 ResourceManager 与 NodeManager，资源改用 Container 描述。v2 的 API 大部分兼容，但配置文件与启停脚本路径都变了。",
 [("v1 的 JobTracker 单点故障会导致整个系统瘫痪", "high",
   "对于JobTracker，存在单点问题，JobTracker如果宕机,整个系统瘫痪"),
  ("v1 的 map 槽与 reduce 槽事先固定，只用其中一种就浪费资源", "high",
   "map槽和reduce槽都是TaskTracker事先存在的，若是MR任务中只存在其中一个（map或是reduce），会出现资源浪费的情况"),
  ("v2 把 JobTracker 拆成 ResourceManager 与 NodeManager，任务监控交给 AppMaster", "high",
   "MR V1中的JobTracker和TaskTracker被替换成相应的Resource Manager，Node Manager"),
  ("v2 用内存量描述资源，比 v1 的 slot 更合理", "high",
   "将资源以内存量的概念来描述，比MR V1中的slot更加合理")],
 ["MapReduce", "YARN", "Container"], ""),

("yarn架构与资源调度",
 "个人资产体系/大数据/yarn/yarn-深入yarn架构和原理.md",
 "YARN 是 Hadoop2 引入的资源调度层，把计算与资源管理解耦，让 MapReduce、Spark、Flink 等框架能跑在同一个集群上。核心四件套：ResourceManager 管全局、ApplicationMaster 管单个应用、NodeManager 管单节点、Container 是资源单位。",
 [("YARN 让多个计算框架可以运行在同一个集群中", "high",
   "YARN的出现，使得多个计算框架运行在一个集群当中。"),
  ("每个应用程序对应一个 ApplicationMaster", "high",
   "每个应用程序对应一个ApplicationMaster。"),
  ("一个 split 对应一个 maptask、一个 container、一个 yarnchild 进程", "high",
   "1个split---->1maptask--->1container--->yarnchild一个划分对应一个maptask，需要一个container资源，对应一个yarnchild进程。"),
  ("YARN 提供 FIFO、Fair、Capacity 三种调度器", "high",
   "FIFO：先提交的程序先执行")],
 ["YARN", "Container", "MapReduce", "Spark"], ""),

("hive日常维护-锁与回收站",
 "个人资产体系/大数据/hive/hive 常用维护语句.md",
 "Hive 运维中最常撞的两件事：表或分区被锁住导致写入失败，以及误删数据要从回收站恢复。前者用 show locks 定位、unlock 释放，后者靠 HDFS 回收站机制。",
 [("锁相关操作靠 show locks 与 unlock 语句处理", "high", "show locks;"),
  ("关闭并发控制要同时改 support.concurrency 与 txn.manager 两个参数", "high",
   "set hive.support.concurrency=false;")],
 ["Hive"], "操作手册类，断言较少"),

("hive调优-引擎切换与参数",
 "个人资产体系/大数据/hive/大数据调优-hive调优.md",
 "Hive 调优先定执行引擎：hive on spark 要配 executor 核数、内存、实例数与并行度；hive on mr 要配 map 内存、Java 堆大小、小表 join 阈值与任务超时。动态分区必须同时开 exec.dynamic.partition 与 nonstrict 模式。",
 [("hive on spark 需要设置执行引擎为 spark 并配置队列", "high",
   "set hive.execution.engine=spark;"),
  ("动态分区要同时打开开关并设为 nonstrict", "high",
   "set hive.exec.dynamic.partition.mode=nonstrict;"),
  ("hive on mr 下小表 join 靠自动转换加文件大小阈值控制", "high",
   "set hive.auto.convert.join = true;")],
 ["Hive", "Spark"], "参数配置类"),

("hive数据存储格式",
 "个人资产体系/大数据/hive/hive 常用数据存储格式.md",
 "Hive 建表时用 STORED AS PARQUET 指定列式存储，相比文本格式查询更快、压缩比更高。建表语句里每个字段都要带 COMMENT，这是元数据的一部分。",
 [("用 STORED AS PARQUET 指定列式存储格式", "high", "STORED AS PARQUET;")],
 ["Hive", "元数据"], "代码片段为主"),

("hiveSQL窗口函数累计",
 "个人资产体系/大数据/hive/hive-sql调优语句.md",
 "按月累计的指标可以用窗口函数一次算出：先用 group by 算出每日值，再用 sum() over (partition by 月 order by 日) 累加，避免自关联。",
 [("按月累计用 sum over partition by trunc(sdate,'MM') order by sdate", "high",
   "over (partition by trunc(sdate,'MM') order by sdate) as indt_plt")],
 ["Hive"], "单条 SQL 示例"),

("hive beeline连接",
 "个人资产体系/大数据/hive/hive beeline.md",
 "beeline 用 JDBC 方式连 HiveServer2，命令格式为 beeline -u jdbc:hive2://host:port/db -n 用户 -w 密码文件。",
 [("beeline 通过 JDBC 连 HiveServer2", "high",
   "beeline -u jdbc:hive2://localhost:10000/default")],
 ["Hive"], "单行命令"),

("hive刷数据到impala",
 "个人资产体系/大数据/impala/hive刷数据到impala.md",
 "Hive 写入数据后 Impala 看不到，因为 Impala 有元数据缓存。要先 invalidate metadata 让元数据失效，再 refresh 刷新单表。",
 [("Impala 看不到 Hive 新写入数据是因为元数据缓存", "medium",
   "由「1.impala-shell -q \"invalidate metadata\" ... 2. REFRESH」两条命令推断，原文未解释原因"),
  ("invalidate metadata 之后还要 refresh 单表", "high",
   "impala-shell - q \"REFRESH dndc.表名\";")],
 ["Hive", "Impala"], ""),

("sqoop导入-hive表头自动拼接",
 "个人资产体系/大数据/etl相关/sqoop/sqoop shell.md",
 "从 pgsql 批量导数据到 Hive 时，最大麻烦是列名对齐：先查 Hive 表结构拿到表头，把空白替换成逗号，再把列名拼进 select 语句，最后交给 sqoop import。这是脚本化的关键思路。（原文含数据库凭据，此处不引用）",
 [("先查 Hive 表头再拼 select 列名，避免列顺序错位", "high",
   "识别hive的表头"),
  ("sqoop import 用 --query 方式导入并指定 target-dir", "high",
   "--target-dir /user/hive/warehouse/")],
 ["Sqoop", "Hive"], "原文含数据库密码，已屏蔽不予引用"),

("sqoop导出到pgsql",
 "个人资产体系/大数据/etl相关/sqoop/sqoop shell-导出pgsql.md",
 "sqoop export 把 Hive 目录数据写回 pgsql。连接串里要加一批参数才稳：defaultRowFetchSize 控制批量、tcpKeepAlive 与 maxReconnects 处理断连、reWriteBatchedInserts 提升批量插入性能。（原文含凭据，此处不引用）",
 [("导出走 sqoop export 并指定 export-dir 与目标表", "high",
   "--table ods_temp_sqoop_test"),
  ("pgsql 连接串需加 keepAlive 与 reconnect 参数保证稳定性", "high",
   "tcpKeepAlive=true&maxReconnects=3")],
 ["Sqoop"], "原文含数据库密码，已屏蔽不予引用"),

("hadoop集群启动流程",
 "个人资产体系/大数据/hadoop运维/大数据运维-hadoop集群启动流程.md",
 "一套 hadoop-3.2.2 加 hbase、hive、zookeeper、spark 的集群启动顺序：先起 zookeeper 三个节点并验证 leader/follower，再起 journalnode、格式化 zkfc 与 namenode、起 standby 做 bootstrapStandby、最后起 datanode 与 yarn。",
 [("先启动 zookeeper 集群并验证 leader/follower 角色", "high",
   "分别在node01、node02、node03 三个节点执行以下命令启动zookeeper"),
  ("standby namenode 要先 bootstrapStandby 再启动", "high",
   "hdfs namenode -bootstrapStandby")],
 ["HDFS", "YARN", "Hadoop集群"], "运维手册"),

("spark调优的十一个方向",
 "个人资产体系/大数据/Spark/大数据调优-spark调优.md",
 "Spark 性能优化按影响面排序：诊断内存消耗、换高性能序列化库、优化数据结构、多次使用的 RDD 做持久化或 checkpoint、GC 调优、提高并行度、广播共享数据、数据本地化、reduceByKey 替代 groupByKey、shuffle 调优。",
 [("多次使用的 RDD 要持久化或 checkpoint", "high",
   "对多次使用的rdd进行持久化或者checkpoint"),
  ("reduceByKey 优于 groupByKey", "high",
   "reducebykey和groupbykey")],
 ["Spark", "RDD"], "清单类，只有要点无展开"),

("大数据资源与论文索引",
 "个人资产体系/大数据/大数据资料/大数据整合-优质资源链接.md",
 "一份大数据学习资源清单：BigData-Notes 笔记库、调优系列博客、谷歌三篇论文、Spark 论文、MapReduce 原理文章。价值在于按主题把入口攒在一起。",
 [("资源按笔记、调优、论文、MapReduce 分类整理", "high", "笔记："),],
 ["Spark", "MapReduce"], "链接清单"),

("HDFS原理-block与packet",
 "个人资产体系/大数据/大数据资料/大数据论文-大数据笔记.md",
 "HDFS 源自 Google GFS 论文。数据组织是三层：文件切成 block 持久化存储，通信时 block 拆成 packet，packet 内含多个 chunk 并各自带 checksum。理解这三层是理解 HDFS 读写与容错的前提。",
 [("HDFS 是根据 Google GFS 论文实现的分布式文件系统", "high",
   "HDFS（Hadoop Distributed File System ）Hadoop分布式文件系统。是根据google发表的论文翻版的。"),
  ("一个文件被拆成多个 block 持久化存储，block 大小由配置决定", "high",
   "一个文件被拆成多个block持续化存储（block size 由配置文件参数决定）"),
  ("通信时一个 block 拆成多个 packet，一个 packet 含多个 chunk", "high",
   "数据通讯过程中一个 block 被拆成 多个 packet")],
 ["HDFS", "MapReduce"], "论文笔记，含大量原理摘录"),

("iceberg初步总结",
 "个人资产体系/大数据/iceberg/iceberg初步总结.md",
 "Iceberg 是数据湖流批一体的解决方案，本质是一种表存储格式：底层用 avro 和 parquet 存数据，向上兼容 flink、spark 计算引擎和 hive、presto、ck 等 OLAP 引擎，以轻量级 jar 包方式集成。",
 [("Iceberg 是数据湖中的一种表存储格式", "high",
   "数据湖中的中间存储格式，一种表存储格式。"),
  ("底层用 avro 与 parquet，以 jar 包方式集成多种引擎", "high",
   "底层是有avro和parquet等格式存储，兼容flink，spark计算引擎和hive、presto、ck等olap引擎")],
 ["Iceberg", "数据湖", "湖仓一体"], ""),

("dataworks数据中台案例",
 "个人资产体系/大数据/dataworks/dataworks数据中台案例.md",
 "列出了几个数据中台落地案例：客如云用 dataphin 解决数据模型与规范建设，另有轻松筹、小打卡、玩吧等；同时记了 ELK 与阿里云 SLS 的日志方案选型。",
 [("dataphin 用于解决数据模型和数据规范建设问题", "high",
   "dataphin可以解决数据模型和数据规范建设问题")],
 ["数据中台"], "案例清单"),

("maxcompute的BI分析链路",
 "个人资产体系/大数据/dataworks/maxcompute的bi分析.md",
 "一条典型的阿里云 BI 链路：web tracking 采集 → log hub 汇聚 → maxcompute 计算 → ADB 分析 → QuickBI 展现。",
 [("BI 链路是 web tracking + log hub + maxcompute + adb + quickbi", "high",
   "总体架构：web tracking + log hub +maxcompute +adb +quickbi")],
 ["数据中台"], "架构清单"),

("电商离线大屏分析架构",
 "个人资产体系/大数据/dataworks/互联网电商的离线大数据大屏或数据看板分析.md",
 "电商看板类项目的一条标准链路：terraform 快速部署云网站，配上阿里云 mysql、dataworks、maxcompute、pgsql、datav。",
 [("看板链路为 mysql + dataworks + maxcompute + pgsql + datav", "high",
   "+阿里云mysql+dataworks+maxcompute+pgsql+datav")],
 ["数据中台"], "架构清单"),

("dataworks赋值节点",
 "个人资产体系/大数据/dataworks/数据赋值节点相关.md",
 "赋值节点的关键差异：输出时系统默认输出一个参数，输入时需要手动设置节点的输入参数才能作为上下文连接。",
 [("赋值节点输出自动，输入需手动设参数", "high",
   "输出时候系统默认输出一个参数，输入时候需要手动设置节点的输入参数作为上下文连接")],
 ["数据中台"], ""),

("数据中台的能力定义",
 "个人资产体系/大数据/数据架构/湖仓相关/数据中台.md",
 "数据中台对数据团队提供的是通用的业务解决方案加通用技术解决方案，对应到数据侧就是可复用的数据业务能力加可复用的数据技术能力。",
 [("中台 = 可复用的业务能力 + 可复用的技术能力", "high",
   "就是提供可复用的数据业务能力+可复用的数据技术能力")],
 ["数据中台"], "短笔记"),
]

def build(title, src, summary, claims, concepts, note):
    stem = f"{T}-{safe(title)}"
    L = ["---", "type: doc", f"title: {title}", f"source_path: raw/docs/{src}",
         "source_type: youdao", "modality: text", "confidence: 0.95",
         "compile_status: compiled", f"compiled_at: {T}", "---", "",
         f"# {title}", "", "## 摘要", "", summary, ""]
    if claims:
        L += ["## 关键断言", ""]
        for stmt, conf, ev in claims:
            L.append(f"- {stmt}  `{conf}`")
            L.append(f"  > 原文：「{ev}」")
            L.append("")
    else:
        L += ["## 关键断言", "", "（本篇为操作记录或清单，无可提炼的断言）", ""]
    if note:
        L += [f"> 注：{note}", ""]
    L += ["## 涉及概念", "", " · ".join(f"[[{c}]]" for c in concepts) if concepts else "（无）", "",
          "## 原文位置", "", f"`raw/docs/{src}`", ""]
    (DOCS / f"{stem}.md").write_text("\n".join(L), encoding="utf-8")
    return stem

made = [build(*p) for p in P]
print(f"✓ 文档页 {len(made)} 篇（本轮大数据域）")
