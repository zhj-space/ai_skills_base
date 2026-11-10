import io
import os
import re

KB = r"D:/workspace/ai_kb_base/second-brain"
CN = re.compile(r"[\u4e00-\u9fa5]")

dirs = []
for r, ds, fs in os.walk(KB):
    if ".obsidian" in r:
        continue
    for d in ds:
        if CN.search(d):
            dirs.append(os.path.join(r, d).replace(KB, "").lstrip("\\/"))
print("中文目录：%d 个 %s" % (len(dirs), dirs[:5]))

bad = []
for r, _, fs in os.walk(KB):
    if ".obsidian" in r:
        continue
    for f in fs:
        if not f.endswith(".md"):
            continue
        p = os.path.join(r, f)
        s = io.open(p, encoding="utf-8").read()
        if not s.startswith("---"):
            continue
        fm = s.split("---", 2)[1]
        for ln in fm.split("\n"):
            if ":" not in ln or ln.strip().startswith("#"):
                continue
            k, v = ln.split(":", 1)
            v = v.strip()
            if not v or CN.search(v) is None:
                continue
            # 允许：页面标题、别名、出处说明等自然语言值
            if k.strip() in ("title", "name", "aliases", "original", "note", "origin",
                             "amended", "summary", "a", "b"):
                continue
            bad.append((k.strip(), v[:34], f))

print("\n非自然语言字段里的中文值：%d 处" % len(bad))
seen = {}
for k, v, f in bad:
    seen.setdefault(k, []).append((v, f))
for k, vs in seen.items():
    print("   字段 %-12s %d 处  例：%s" % (k, len(vs), vs[0][0]))

# 关系段是否还有中文标签
CN_LABEL = re.compile(r"^-\s*([^：:]{1,24})\s*[：:]")
LEFT = []
for r, _, fs in os.walk(os.path.join(KB, "wiki")):
    for f in fs:
        if not f.endswith(".md"):
            continue
        s = io.open(os.path.join(r, f), encoding="utf-8").read()
        if "## 关系" not in s:
            continue
        seg = s.split("## 关系", 1)[1].split("\n## ", 1)[0]
        for ln in seg.split("\n"):
            m = CN_LABEL.match(ln.strip())
            if m and CN.search(m.group(1)):
                LEFT.append((f, m.group(1)))
print("\n关系段残留中文标签：%d 处 %s" % (len(LEFT), LEFT[:5]))
