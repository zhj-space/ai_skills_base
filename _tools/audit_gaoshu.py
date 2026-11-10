# -*- coding: utf-8 -*-
"""按规则逐项核对本次整理是否符合规范，输出可核验的数据"""
import io, json, os, re, subprocess, sys

WS = r"D:/workspace/ai_kb_base"
KB = os.path.join(WS, "second-brain")
TOOLS = os.path.join(WS, "_tools")
SRC = os.path.join(KB, "raw", "summaries", "个人资产体系", "数学", "同济版高数知识点梳理.md")

ITEMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_items.json"), encoding="utf-8"))
raw = io.open(SRC, encoding="utf-8").read()

CONCEPTS = ["极限","连续与间断","导数与微分","中值定理","泰勒公式","不定积分","定积分",
            "牛顿-莱布尼茨公式","微元法","微分方程","向量代数","偏导数与全微分","梯度",
            "重积分","曲线曲面积分","格林高斯斯托克斯公式","无穷级数"]
DOCS = ["2026-11-06-同济版高数知识点梳理.md", "2026-11-07-高数知识点总索引.md"]

print("=" * 62)
print("一、原文结构")
print("=" * 62)
chaps = [l[3:].strip() for l in raw.split("\n") if l.startswith("## ")]
math_chaps = [c for c in chaps if c not in ("全书主线：三个问题，一条链", "学习路线建议")]
print("原文 ## 级标题：%d 个" % len(chaps))
print("  其中数学章节：%d 个" % len(math_chaps))
print("  另有两章为全书导览：全书主线、学习路线建议")
print("编号小节（x.y）：%d 个" % len(ITEMS))
print("原文规模：%d 行 / %d 字" % (raw.count("\n")+1,
      len(re.search(r"word_count:\s*(\d+)", raw).group(1))))

print()
print("=" * 62)
print("二、知识点颗粒度")
print("=" * 62)
tp = sum(len(x["性质"]) for x in ITEMS)
tu = sum(len(x["用处"]) for x in ITEMS)
print("定义：%d 条（每节 1 条）" % len(ITEMS))
print("性质：%d 条" % tp)
print("用处：%d 条" % tu)
print("合计知识点：%d 条" % (len(ITEMS)+tp+tu))

print()
print("=" * 62)
print("三、生成物")
print("=" * 62)
tot_l = tot_b = 0
for d in DOCS:
    p = os.path.join(KB, "wiki", "summaries", d)
    s = io.open(p, encoding="utf-8").read()
    n = len(re.findall(r"^\- .*`(high|medium|low)`\s*$", s, re.M))
    tot_l += s.count("\n")+1; tot_b += len(s.encode("utf-8"))
    print("文档页 %-40s %4d 行 %6.1f KB %3d 断言" % (d[:38], s.count("\n")+1, len(s.encode("utf-8"))/1024, n))
cl = cb = 0
for c in CONCEPTS:
    p = os.path.join(KB, "wiki", "concepts", c + ".md")
    s = io.open(p, encoding="utf-8").read()
    cl += s.count("\n")+1; cb += len(s.encode("utf-8"))
print("概念页 17 张：%d 行 / %.1f KB" % (cl, cb/1024))
print("合计：%d 行 / %.1f KB" % (tot_l+cl, (tot_b+cb)/1024))

print()
print("=" * 62)
print("四、规则核对")
print("=" * 62)

# 1 编号完整性
expected = {}
for it in ITEMS:
    for k in range(1, len(it["性质"])+1): expected["%s-P%d" % (it["no"], k)] = 1
    for k in range(1, len(it["用处"])+1): expected["%s-U%d" % (it["no"], k)] = 1
found = set()
for d in (os.path.join(KB,"wiki","concepts"), os.path.join(KB,"wiki","summaries")):
    for fn in os.listdir(d):
        if fn.endswith(".md"):
            found |= set(re.findall(r"`([0-9]+\.[0-9]+-[PU]\d+)`",
                        io.open(os.path.join(d, fn), encoding="utf-8").read()))
miss = set(expected) - found
extra = set(found) - set(expected)
print("[1] 知识点编号：应有 %d，实有 %d，缺 %d，多 %d  → %s"
      % (len(expected), len(found), len(miss), len(extra), "通过" if not miss and not extra else "不通过"))

# 2 每章每节是否都有归属概念页
MAP = {"极限":["1.1","1.2","1.3","1.4"],"连续与间断":["1.5","1.6"],"导数与微分":["2.1","2.2","2.3","2.4"],
 "中值定理":["3.1","3.2","3.3","3.5","3.6"],"泰勒公式":["3.4"],"不定积分":["4.1","4.2","4.3","4.4"],
 "定积分":["5.1","5.2","5.5"],"牛顿-莱布尼茨公式":["5.3","5.4"],"微元法":["6.1","6.2","6.3"],
 "微分方程":["7.1","7.2","7.3","7.4"],"向量代数":["8.1","8.2","8.3","8.4"],
 "偏导数与全微分":["9.1","9.2","9.3","9.4"],"梯度":["9.5","9.6"],
 "重积分":["10.1","10.2","10.3","10.4"],"曲线曲面积分":["11.1","11.2","11.5"],
 "格林高斯斯托克斯公式":["11.3","11.4","11.6"],"无穷级数":["12.1","12.2","12.3","12.4","12.5"]}
owned = set(n for v in MAP.values() for n in v)
allno = set(x["no"] for x in ITEMS)
print("[2] 节级归属：57 节中 %d 节有明确归属，未归属 %d  → %s"
      % (len(owned), len(allno-owned), "通过" if not (allno-owned) else "不通过"))

# 3 保留率
pages = [os.path.join(KB,"wiki","concepts",c+".md") for c in CONCEPTS] + \
        [os.path.join(KB,"wiki","summaries",d) for d in DOCS]
cov = subprocess.run([sys.executable, os.path.join(TOOLS,"check_coverage.py"), SRC] + pages,
                     capture_output=True, text=True).stdout
m = re.search(r"实质内容保留率：([\d.]+)%", cov)
m2 = re.search(r"实质内容未保留行数：(\d+)", cov)
print("[3] 实质保留率：%s（未保留 %s 行）→ %s"
      % (m.group(1) if m else "?", m2.group(1) if m2 else "?",
         "通过" if m and float(m.group(1)) >= 99 else "不通过"))

# 4 断言校验
cl_out = subprocess.run([sys.executable, os.path.join(TOOLS,"check_claims.py"),"--all"],
                        capture_output=True, text=True).stdout
m3 = re.search(r"逐字通过 (\d+) 条 / 不匹配 (\d+) 条", cl_out)
print("[4] 断言逐字校验：%s 条通过，%s 条不匹配 → %s"
      % (m3.group(1), m3.group(2), "通过" if m3 and m3.group(2)=="0" else "不通过"))

# 5 index 是否含
idx = io.open(os.path.join(KB,"index.md"), encoding="utf-8").read()
ok = all(("[[%s]]" % c) in idx for c in CONCEPTS)
print("[5] index 是否收录 17 张概念页：%s" % ("通过" if ok else "不通过"))
ok2 = all(d[:-3] in idx for d in DOCS)
print("[6] index 是否收录 2 篇文档页：%s" % ("通过" if ok2 else "不通过"))

# 6 主题地图是否含
tm = io.open(os.path.join(KB,"wiki","topic-map.md"), encoding="utf-8").read()
ok3 = all(("[[%s]]" % c) in tm for c in CONCEPTS)
print("[7] 主题地图是否收录 17 张概念页：%s" % ("通过" if ok3 else "不通过"))

# 7 库根是否只有规则内文件
root = sorted(os.listdir(KB))
allowed = {"agent.md","index.md","ontology.json","wiki","raw","attachments",".obsidian"}
viol = [x for x in root if x not in allowed]
print("[8] 库根文件：%s → %s" % (root, "通过" if not viol else "存在规则外文件 %s" % viol))

# 8 日志
logs = os.path.join(WS, "logs")
print("[9] 处理日志：%s" % (os.listdir(logs) if os.path.isdir(logs) else "缺失"))
