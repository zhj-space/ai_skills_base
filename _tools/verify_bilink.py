import io, os, re

KB = r"D:/workspace/ai_kb_base/second-brain"
CD = os.path.join(KB, "wiki", "concepts")
DD = os.path.join(KB, "wiki", "summaries")
tm = io.open(os.path.join(KB, "wiki", "topic-map.md"), encoding="utf-8").read()
idx = io.open(os.path.join(KB, "index.md"), encoding="utf-8").read()

C = set(f[:-3] for f in os.listdir(CD) if f.endswith(".md"))
D = set(f[:-3] for f in os.listdir(DD) if f.endswith(".md"))
lk_t = set(re.findall(r"\[\[([^\]|#]+)", tm))
lk_i = set(re.findall(r"\[\[([^\]|#]+)", idx))

print("主题地图：概念页 %d / %d，缺 %s" % (len(C & lk_t), len(C), sorted(C - lk_t) or "无"))
print("index：概念 %d / %d，文档 %d / %d，缺 %s" %
      (len(C & lk_i), len(C), len(D & lk_i), len(D), sorted(D - lk_i) or "无"))

# 文档页有链接比例
n = 0
for f in D:
    s = io.open(os.path.join(DD, f + ".md"), encoding="utf-8").read()
    seg = s.split("## 涉及概念")[1].split("\n## ")[0]
    if "[[" in seg:
        n += 1
print("\n文档页挂概念：%d / %d = %.0f%%" % (n, len(D), n * 100.0 / len(D)))

# 概念页被文档页反向命中
hit = {}
for f in D:
    s = io.open(os.path.join(DD, f + ".md"), encoding="utf-8").read()
    seg = s.split("## 涉及概念")[1].split("\n## ")[0]
    for t in re.findall(r"\[\[([^\]|#]+)", seg):
        hit[t] = hit.get(t, 0) + 1
print("被文档页引用的概念页：%d / %d" % (len(hit), len(C)))
print("零文档引用的概念页：%s" % (sorted(C - set(hit)) or "无"))
top = sorted(hit.items(), key=lambda x: -x[1])[:8]
print("最常被挂的概念页：" + "、".join("%s(%d)" % (k, v) for k, v in top))
