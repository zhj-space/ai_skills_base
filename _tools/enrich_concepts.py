# -*- coding: utf-8 -*-
"""为概念页补「核心定义与公式」「定理与运算律」两节：直接取原文定义段与性质段"""
import io, json, os

KB = r"D:/workspace/ai_kb_base/second-brain"
TOOLS = r"D:/workspace/ai_kb_base/_tools"
CDIR = os.path.join(KB, "wiki", "concepts")
ITEMS = json.load(io.open(os.path.join(TOOLS, "gaoshu_items.json"), encoding="utf-8"))
BY_NO = {it["no"]: it for it in ITEMS}

MAP = {
 "极限": ["1.1","1.2","1.3","1.4"],
 "连续与间断": ["1.5","1.6"],
 "导数与微分": ["2.1","2.2","2.3","2.4"],
 "中值定理": ["3.1","3.2","3.3"],
 "泰勒公式": ["3.4"],
 "不定积分": ["4.1","4.2","4.3","4.4"],
 "定积分": ["5.1","5.2","5.5"],
 "牛顿-莱布尼茨公式": ["5.3","5.4"],
 "微元法": ["6.1","6.2","6.3"],
 "微分方程": ["7.1","7.2","7.3","7.4"],
 "向量代数": ["8.1","8.2","8.3","8.4"],
 "偏导数与全微分": ["9.1","9.2","9.3","9.4"],
 "梯度": ["9.5","9.6"],
 "重积分": ["10.1","10.2","10.3","10.4"],
 "曲线曲面积分": ["11.1","11.2","11.5"],
 "格林高斯斯托克斯公式": ["11.3","11.4","11.6"],
 "无穷级数": ["12.1","12.2","12.3","12.4","12.5"],
}

def render_block(nos, kind):
    out = []
    for no in nos:
        it = BY_NO[no]
        body = it[kind]
        if not body:
            continue
        out.append("**%s %s**" % (no, it["raw"]))
        out.append("")
        for x in body:
            out.append(x if x.startswith("-") or x.startswith("|") else x)
            out.append("")
    return "\n".join(out).rstrip() + "\n"

n_ok = 0
for name, nos in MAP.items():
    p = os.path.join(CDIR, name + ".md")
    s = io.open(p, encoding="utf-8").read()
    if "## 核心定义与公式" in s:
        print("SKIP %s（已有）" % name); continue

    defs = render_block(nos, "定义")
    props = render_block(nos, "性质")

    block = "## 核心定义与公式\n\n" + defs + "\n"
    tail = "\n## 定理与运算律\n\n" + props + "\n"

    # 定义与公式：插在「## 是什么」之前
    assert "## 是什么" in s, name
    s = s.replace("## 是什么", block + "\n## 是什么", 1)
    # 定理与运算律：插在「## 怎么用」之前
    assert "## 怎么用" in s, name
    s = s.replace("## 怎么用", tail + "\n## 怎么用", 1)

    io.open(p, "w", encoding="utf-8", newline="").write(s)
    n_ok += 1
    print("OK  %-16s +%d 行 -> %d 行" % (name, (block + tail).count("\n"), s.count("\n") + 1))

print("\n已补 %d 页" % n_ok)
