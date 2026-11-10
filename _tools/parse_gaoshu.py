# -*- coding: utf-8 -*-
"""把原文 57 个知识点条目解析成结构化 JSON（定义/为什么/性质/用处 四段完整保留）"""
import io, re, json

SRC = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/数学/同济版高数知识点梳理.md"
s = io.open(SRC, encoding="utf-8").read()
lines = s.split("\n")

# 1) 定位章与条目起点
CHAPTERS = []
ITEMS = []
for i, ln in enumerate(lines):
    t = ln.strip()
    if ln.startswith("## "):
        CHAPTERS.append((i, ln[3:].strip()))
        continue
    m = re.match(r"^(\d+\.\d+)([^\s].{1,40})$", t)
    if m:
        ITEMS.append({"no": m.group(1), "raw": m.group(2).strip(), "start": i})

def chapter_of(lineno):
    cur = ""
    for li, name in CHAPTERS:
        if li < lineno:
            cur = name
        else:
            break
    return cur

# 2) 切段：每个条目从 start 到下一个条目 start（或下一章）
SEG = {"定义": [], "为什么": [], "性质": [], "用处": []}
out = []
for k, it in enumerate(ITEMS):
    end = ITEMS[k+1]["start"] if k+1 < len(ITEMS) else len(lines)
    # 不能跨章
    for li, name in CHAPTERS:
        if it["start"] < li < end:
            end = li
            break
    body = lines[it["start"]+1:end]

    cur = None
    buckets = {"定义": [], "为什么": [], "性质": [], "用处": [], "章末小结": []}
    # 章末小结的起始标记（原文每章末尾的串联/概括段）
    TAIL_HEADS = ("本章串联", "用一句话概括", "全章只有", "全章的逻辑",
                  "这一章本质", "做题前先问", "把四个公式并排", "两条线：")
    for ln in body:
        t = ln.strip()
        if t.startswith("定义 ·") or t.startswith("定义·"):
            cur = "定义"; continue
        if t.startswith("为什么 ·") or t.startswith("为什么·"):
            cur = "为什么"; continue
        if t.startswith("性质 ·") or t.startswith("性质·"):
            cur = "性质"; continue
        if t.startswith("用处 ·") or t.startswith("用处·"):
            cur = "用处"; continue
        if any(t.startswith(h) for h in TAIL_HEADS):
            cur = "章末小结"
            buckets[cur].append(t)
            continue
        if cur == "章末小结":
            if t and not re.match(r"^CH\s*\d", t):
                buckets[cur].append(t)
            continue
        if cur and t:
            buckets[cur].append(t)

    out.append({
        "ch": chapter_of(it["start"]),
        "no": it["no"],
        "raw": it["raw"],
        "定义": buckets["定义"],
        "为什么": buckets["为什么"],
        "性质": buckets["性质"],
        "用处": buckets["用处"],
        "章末小结": buckets["章末小结"],
    })

with io.open(r"D:/workspace/ai_kb_base/_tools/gaoshu_items.json", "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))

# 3) 自检
print("条目数：%d\n" % len(out))
tot = 0
for o in out:
    n = sum(len(o[k]) for k in ("定义", "为什么", "性质", "用处"))
    tot += n
    print("%-4s %-32s 定义%2d 为什么%2d 性质%2d 用处%2d" % (
        o["no"], o["raw"][:30], len(o["定义"]), len(o["为什么"]), len(o["性质"]), len(o["用处"])))
print("\n正文行合计：%d" % tot)
