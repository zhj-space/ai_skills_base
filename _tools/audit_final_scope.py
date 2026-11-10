import io
import os
import re

KB = r"D:/workspace/ai_kb_base/second-brain"


def walk(sub=""):
    root = os.path.join(KB, sub) if sub else KB
    out = []
    for r, _, fs in os.walk(root):
        if ".obsidian" in r:
            continue
        for f in fs:
            if f.endswith(".md"):
                out.append(os.path.join(r, f))
    return out


allmd = walk()
con = [p for p in allmd if os.sep + "wiki" + os.sep + "concepts" + os.sep in p]
doc = [p for p in allmd if os.sep + "wiki" + os.sep + "summaries" + os.sep in p]
dig = [p for p in allmd if os.sep + "wiki" + os.sep + "analysis" + os.sep in p]
tpl = [p for p in allmd if "_templates" in p]
src = [p for p in allmd if os.sep + "raw" + os.sep in p]
rootmd = [p for p in allmd if os.path.dirname(p) == KB]

print("=== 全库 md 归属 ===")
print("概念页 %3d  ← 本体 C1~C9" % len(con))
print("文档页 %3d  ← 本体 D1" % len(doc))
print("沉淀页 %3d  ← 本体 G1" % len(dig))
print("模板   %3d  ← 不在范围（含占位符）" % len(tpl))
print("库根   %3d  ← 不在范围（索引/地图/规则）" % len(rootmd))
print("sources %3d ← 原始层，按设计不受本体约束" % len(src))
print("合计   %3d" % len(allmd))
print("受本体约束：%d / %d = %.0f%%" % (len(con) + len(doc) + len(dig), len(allmd),
                                       (len(con) + len(doc) + len(dig)) * 100.0 / len(allmd)))

# 合规但带「已声明缺口」的页
n_link = n_exempt = 0
for p in doc:
    s = io.open(p, encoding="utf-8").read()
    seg = s.split("## 涉及概念", 1)[1].split("\n## ", 1)[0] if "## 涉及概念" in s else ""
    if "[[" in seg:
        n_link += 1
    else:
        n_exempt += 1
print("\n=== 文档页「涉及概念」实况 ===")
print("挂上概念（真链）  %3d" % n_link)
print("豁免声明（未挂接）%3d" % n_exempt)

n_gap = 0
for p in con:
    s = io.open(p, encoding="utf-8").read()
    if "信息缺口" in s:
        n_gap += 1
print("\n=== 概念页实况 ===")
print("声明了信息缺口    %3d / %d" % (n_gap, len(con)))
et = {}
for p in con:
    m = re.search(r"^entity_type:[ \t]*(\S+)", io.open(p, encoding="utf-8").read(), re.M)
    k = m.group(1) if m else "(无)"
    et[k] = et.get(k, 0) + 1
print("类分布：" + " · ".join("%s %d" % (k, v) for k, v in sorted(et.items(), key=lambda x: -x[1])))
