"""按新语义重构 type / entity_type 两个字段。

新语义：
  type        = 页面大类：concept / entity / method / metric（知识节点）+ doc / digest / index
  entity_type = 实体子类，只在 type=entity 的页面出现

旧语义（本次要废弃）：
  type: node + entity_type: concept/entity/method/metric

用法：python migrate_type_field.py --dry | --apply
"""
import io, os, re, sys

KB = r"D:/workspace/ai_kb_base/second-brain"
NODE_DIRS = ["concepts", "entities", "methods", "metrics"]

# 11 个实体的子类（值英文，与目录/属性全英文的口径一致）
ENTITY_SUBTYPE = {
    "HDFS": "distributed_storage",
    "Spark": "compute_engine",
    "MapReduce": "compute_engine",
    "Hive": "data_warehouse",
    "Kafka": "message_queue",
    "YARN": "resource_scheduler",
    "Sqoop": "data_transfer",
    "Iceberg": "table_format",
    "pgsql": "relational_database",
    "SQLServer": "relational_database",
    "JVM": "runtime",
}

DRY = "--apply" not in sys.argv


def main():
    ok = skip = 0
    for d in NODE_DIRS:
        p = os.path.join(KB, "wiki", d)
        for f in sorted(os.listdir(p)):
            if not f.endswith(".md"):
                continue
            name = f[:-3]
            path = os.path.join(p, f)
            s = io.open(path, encoding="utf-8").read()

            mt = re.search(r"^type:[ \t]*(\S+)[ \t]*$", s, re.M)
            me = re.search(r"^entity_type:[ \t]*(\S+)[ \t]*$", s, re.M)
            if not mt:
                print("  !! 无 type  %s" % name)
                skip += 1
                continue

            old_type = mt.group(1)
            old_et = me.group(1) if me else None
            if old_type != "node":
                print("  -- 已是新语义 %-14s type=%s" % (name, old_type))
                skip += 1
                continue

            # 大类取自旧 entity_type；缺失时按所在目录推断
            new_type = old_et if old_et in ("concept", "entity", "method", "metric") else {
                "concepts": "concept", "entities": "entity",
                "methods": "method", "metrics": "metric"}[d]

            if new_type == "entity":
                sub = ENTITY_SUBTYPE.get(name)
                if not sub:
                    print("  !! 实体缺子类映射  %s" % name)
                    skip += 1
                    continue
                s = s[:mt.start()] + "type: entity" + s[mt.end():]
                # 重新定位 entity_type（前面替换改了偏移）
                me = re.search(r"^entity_type:[ \t]*(\S+)[ \t]*$", s, re.M)
                s = s[:me.start()] + "entity_type: " + sub + s[me.end():]
                note = "entity/%s" % sub
            else:
                s = s[:mt.start()] + "type: " + new_type + s[mt.end():]
                me = re.search(r"^entity_type:[^\n]*\n", s, re.M)
                if me:
                    s = s[:me.start()] + s[me.end():]
                note = new_type

            if not DRY:
                io.open(path, "w", encoding="utf-8", newline="").write(s)
            print("  OK %-14s node/%s -> %s" % (name, old_et or "?", note))
            ok += 1

    print("\n%s：改 %d 页，跳过 %d 页" % ("预演" if DRY else "已落盘", ok, skip))


if __name__ == "__main__":
    main()
