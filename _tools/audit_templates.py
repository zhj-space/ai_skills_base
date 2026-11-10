import io, os, re

KB = r"D:/workspace/ai_kb_base/second-brain"
TD = os.path.join(KB, "wiki", "_templates")

real = set(f for f in os.listdir(TD) if f.endswith(".md"))
print("=== 模板目录实有 %d 个 ===" % len(real))
for f in sorted(real):
    p = os.path.join(TD, f)
    s = io.open(p, encoding="utf-8").read()
    mt = re.search(r"^type:[ \t]*(\S+)", s, re.M)
    segs = re.findall(r"^## (.+)$", s, re.M)
    print("  %-24s type=%-8s %d 段" % (f, mt.group(1) if mt else "缺", len(segs)))

print("\n=== agent.md 模板表引用的文件是否都存在 ===")
s = io.open(os.path.join(KB, "agent.md"), encoding="utf-8").read()
refs = set(re.findall(r"_templates/([a-z-]+\.md)", s))
for r in sorted(refs):
    print("  %-26s %s" % (r, "OK" if r in real else "!! 不存在"))

print("\n=== 有模板但 agent.md 没引用 ===")
miss = real - refs
print("  " + (", ".join(sorted(miss)) if miss else "无"))

print("\n=== 四类节点目录的页面是否都有对应类模板可套 ===")
for d, tp in (("concepts", "concept"), ("entities", "entity"),
              ("methods", "method"), ("metrics", "metric")):
    tpl = "%s-template.md" % tp
    print("  wiki/%-9s -> %-22s %s" % (d, tpl, "OK" if tpl in real else "!! 缺"))
