import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
DIRS = {"concepts": "概念", "entities": "实体", "methods": "方法",
        "metrics": "指标", "summaries": "文档", "analysis": "沉淀"}

print("=== 各目录 type / entity_type 分布 ===")
for d in DIRS:
    p = os.path.join(KB, "wiki", d)
    tp = collections.Counter()
    et = collections.Counter()
    n = 0
    for f in sorted(os.listdir(p)):
        if not f.endswith(".md"):
            continue
        n += 1
        s = io.open(os.path.join(p, f), encoding="utf-8").read()
        m = re.search(r"^type:[ \t]*(\S+)", s, re.M)
        tp[m.group(1) if m else "(缺)"] += 1
        m2 = re.search(r"^entity_type:[ \t]*(\S+)", s, re.M)
        et[m2.group(1) if m2 else "(缺)"] += 1
    print("%-10s %3d 页  type=%s" % (d, n, dict(tp)))
    print("%-10s         entity_type=%s" % ("", dict(et)))

print("\n=== 11 个实体页现状 ===")
p = os.path.join(KB, "wiki", "entities")
for f in sorted(os.listdir(p)):
    if not f.endswith(".md"):
        continue
    s = io.open(os.path.join(p, f), encoding="utf-8").read()
    t = re.search(r"^type:[ \t]*(\S+)", s, re.M)
    e = re.search(r"^entity_type:[ \t]*(\S+)", s, re.M)
    print("  %-12s type=%-6s entity_type=%s" % (f[:-3], t.group(1) if t else "缺", e.group(1) if e else "缺"))

print("\n=== 生成器/模板里写死的字段 ===")
TARGETS = [
    r"D:/workspace/ai_kb_base/_tools/build_concepts.py",
    r"D:/workspace/ai_kb_base/_tools/compile_image_notes.py",
    r"D:/workspace/ai_kb_base/_tools/compile_short_notes.py",
    r"D:/workspace/ai_kb_base/_tools/batch_doc.py",
]
for p in TARGETS:
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    hits = [(i + 1, ln.strip()) for i, ln in enumerate(s.split("\n"))
            if re.search(r"type:|entity_type", ln)]
    if hits:
        print("--- %s" % os.path.basename(p))
        for no, ln in hits[:8]:
            print("    %4d %s" % (no, ln[:80]))

print("\n=== 模板文件的 frontmatter ===")
TD = os.path.join(KB, "wiki", "_templates")
for f in sorted(os.listdir(TD)):
    if not f.endswith(".md"):
        continue
    s = io.open(os.path.join(TD, f), encoding="utf-8").read()
    head = s.split("---")[1] if s.startswith("---") else s[:200]
    lines = [ln for ln in head.split("\n") if ln.strip()]
    print("--- %s" % f)
    for ln in lines[:8]:
        print("    " + ln[:70])
