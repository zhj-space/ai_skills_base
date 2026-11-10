import io
import os
import re

CD = r"D:/workspace/ai_kb_base/second-brain/wiki/概念"
C = sorted(f[:-3] for f in os.listdir(CD) if f.endswith(".md"))
PROD = ["HDFS", "Spark", "Hive", "Kafka", "Iceberg", "Sqoop", "YARN",
        "MapReduce", "pgsql", "SQLServer", "JVM", "DataWorks", "Flink", "Hudi"]

print("=== 概念页正文里提到了哪些产品（=该概念的外延）===")
for c in C:
    s = io.open(os.path.join(CD, c + ".md"), encoding="utf-8").read()
    hit = [p for p in PROD if re.search(r"\b" + p + r"\b", s) or p in s]
    if len(hit) >= 2:
        print("   %-16s 提到 %d 个：%s" % (c, len(hit), "、".join(hit)))

print("\n=== 现有「上位」两端都是概念的（类型包含）抽查 ===")
n = 0
for c in C:
    s = io.open(os.path.join(CD, c + ".md"), encoding="utf-8").read()
    if "## 关系" not in s:
        continue
    seg = s.split("## 关系", 1)[1].split("\n## ", 1)[0]
    for ln in seg.split("\n"):
        if ln.strip().startswith("- 上位："):
            n += 1
print("   上位关系共 %d 条" % n)

print("\n=== 是否存在「实体 → 概念」的实例化写法（目前应无）===")
inst = 0
for c in C:
    s = io.open(os.path.join(CD, c + ".md"), encoding="utf-8").read()
    for m in re.findall(r"实例化为|是.*的实例|的实例是", s):
        inst += 1
print("   显式写「实例」字样的：%d 处" % inst)
