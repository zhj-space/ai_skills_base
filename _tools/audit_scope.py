import io
import os
import re

KB = r"D:/workspace/ai_kb_base/second-brain"
CD = os.path.join(KB, "wiki", "concepts")
DD = os.path.join(KB, "wiki", "summaries")
GD = os.path.join(KB, "wiki", "analysis")


def mds(d):
    p = d if os.path.isabs(d) else os.path.join(KB, d)
    return sorted(f[:-3] for f in os.listdir(p) if f.endswith(".md"))


def read(p):
    return io.open(p, encoding="utf-8").read()


def sec(s, name):
    if name not in s:
        return ""
    return s.split(name, 1)[1].split("\n## ", 1)[0]


C, D, G = mds(CD), mds(DD), mds(GD)
print("=== 本体 scope 覆盖范围 ===")
print("概念页 %3d  ← 在 scope 内（entity_type + 关系段）" % len(C))
print("文档页 %3d  ← scope 外（无 entity_type，不受 7 约束）" % len(D))
print("沉淀页 %3d  ← scope 外" % len(G))

print("\n=== 11 个实体页：正文是否写了「版本 / 边界 / 可替代」 ===")
hdr = "%-14s %-4s %-4s %-4s %s"
print(hdr % ("页面", "版本", "边界", "替代", "判定"))
VER = re.compile(r"版本|v?\d+\.\d+|7\.x|3\.x|8/11/17|发行版|升级|停更|停止维护|EOL")
EDGE = re.compile(r"不适用|不适合|不擅长|不支持|限制|边界|做不到|代价是|瓶颈|单点")
REPL = re.compile(r"替代|换成|迁移到|对比|相比|选型")
bad = []
for c in C:
    s = read(os.path.join(CD, c + ".md"))
    if not re.search(r"^entity_type:[ \t]*实体$", s, re.M):
        continue
    body = sec(s, "## 有什么性质") + sec(s, "## 常见误区") + sec(s, "## 怎么用")
    v, e, r = bool(VER.search(body)), bool(EDGE.search(body)), bool(REPL.search(body))
    tag = "OK" if (e or r) else "缺边界"
    if tag != "OK":
        bad.append(c)
    print(hdr % (c, "有" if v else "—", "有" if e else "—", "有" if r else "—", tag))
print("\n正文未对齐实体文风的页：%d / 11" % len(bad))

print("\n=== 2 个指标页：是否写了口径（公式 / 单位 / 时间窗） ===")
for c in C:
    s = read(os.path.join(CD, c + ".md"))
    if not re.search(r"^entity_type:[ \t]*指标$", s, re.M):
        continue
    body = sec(s, "## 是什么") + sec(s, "## 有什么性质")
    f = bool(re.search(r"=|\+|公式|口径", body))
    u = bool(re.search(r"单位|次/秒|TPS|QPS|条|个", body))
    t = bool(re.search(r"时间|周期|窗口|最近 \d+|每天|日|月", body))
    print("   %-10s 公式=%s 单位=%s 时间窗=%s" % (c, "有" if f else "—", "有" if u else "—", "有" if t else "—"))

print("\n=== 只有「相关」没有结构关系的页（建模偏弱） ===")
weak = []
for c in C:
    s = read(os.path.join(CD, c + ".md"))
    seg = sec(s, "## 关系")
    labels = set(re.findall(r"^-\s*([^：:]{1,10})\s*[：:]", seg, re.M))
    strong = labels - {"相关", "出处文档"}
    if not strong:
        weak.append((c, len(labels)))
print("   共 %d 页：%s" % (len(weak), "、".join(x[0] for x in weak[:12])))
