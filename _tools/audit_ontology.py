import io, os, re, collections

KB = r"D:/workspace/ai_kb_base/second-brain"
CD = os.path.join(KB, "wiki", "concepts")
DD = os.path.join(KB, "wiki", "summaries")

C = sorted(f[:-3] for f in os.listdir(CD) if f.endswith(".md"))
D = sorted(f[:-3] for f in os.listdir(DD) if f.endswith(".md"))


def read(p):
    return io.open(p, encoding="utf-8").read()


def fm(s):
    if not s.startswith("---"):
        return {}
    body = s.split("---", 2)[1]
    out = {}
    for ln in body.split("\n"):
        if ":" in ln and not ln.strip().startswith("#"):
            k, v = ln.split(":", 1)
            out[k.strip()] = v.strip()
    return out


et = collections.Counter()
keys = collections.Counter()
alias_cnt = 0
for c in C:
    s = read(os.path.join(CD, c + ".md"))
    f = fm(s)
    et[f.get("entity_type", "(无)")] += 1
    for k in f:
        keys[k] += 1
    if f.get("aliases") and f["aliases"] not in ("[]", ""):
        alias_cnt += 1

print("=== 概念页 entity_type 分布 ===")
for k, v in et.most_common():
    print("   %-10s %3d" % (k, v))
print("\n=== frontmatter 字段使用频次 ===")
for k, v in keys.most_common():
    print("   %-14s %3d / %d" % (k, v, len(C)))
print("有 aliases 的概念页：%d" % alias_cnt)

print("\n=== 关系段用到的关系标签 ===")
lab = collections.Counter()
sample = collections.defaultdict(list)
for c in C:
    s = read(os.path.join(CD, c + ".md"))
    if "## 关系" not in s:
        continue
    seg = s.split("## 关系", 1)[1].split("\n## ", 1)[0]
    for ln in seg.split("\n"):
        m = re.match(r"^-\s*([^：:]{2,8})\s*[：:]", ln.strip())
        if m:
            lab[m.group(1).strip()] += 1
            if len(sample[m.group(1).strip()]) < 2:
                sample[m.group(1).strip()].append(c)
for k, v in lab.most_common(24):
    print("   %-10s %3d   e.g. %s" % (k, v, "、".join(sample[k])))

print("\n=== 文档页 frontmatter 字段 ===")
dk = collections.Counter()
for d in D:
    for k in fm(read(os.path.join(DD, d + ".md"))):
        dk[k] += 1
for k, v in dk.most_common():
    print("   %-16s %3d / %d" % (k, v, len(D)))
