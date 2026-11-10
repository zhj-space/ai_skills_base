# -*- coding: utf-8 -*-
"""按建卡门槛第 1 条核对：每个候选概念在库内被多少篇 source 涉及"""
import os, io, re

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw")

# 候选概念 -> 关键词（用于统计涉及篇数）
CAND = {
    "极限": ["极限", "ε-N", "ε-δ", "收敛"],
    "导数与微分": ["导数", "微分", "可导", "切线斜率"],
    "中值定理": ["中值定理", "罗尔", "拉格朗日", "柯西", "泰勒"],
    "不定积分": ["不定积分", "原函数"],
    "定积分": ["定积分", "黎曼和"],
    "微积分基本定理": ["牛顿-莱布尼茨", "基本定理"],
    "微元法": ["微元法", "元素法"],
    "微分方程": ["微分方程"],
    "向量代数": ["数量积", "向量积", "点积", "叉积"],
    "偏导数与全微分": ["偏导数", "全微分", "偏导"],
    "重积分": ["重积分", "二重积分", "三重积分"],
    "曲线曲面积分": ["曲线积分", "曲面积分", "格林公式", "高斯公式", "斯托克斯"],
    "无穷级数": ["级数", "幂级数", "傅里叶"],
}

files = []
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if fn.endswith(".md"):
            files.append(os.path.join(root, fn))

print("sources 总篇数：%d\n" % len(files))
print("%-16s %6s  %s" % ("concepts", "涉及篇数", "涉及的其它篇（最多列5个）"))
print("-" * 78)

EXCLUDE = "同济版高数知识点梳理"
for name, kws in CAND.items():
    hit = []
    for p in files:
        if EXCLUDE in p:
            continue
        s = io.open(p, encoding="utf-8", errors="ignore").read()
        if any(k in s for k in kws):
            hit.append(os.path.basename(p)[:-3])
    flag = "✓ 过门槛" if len(hit) >= 2 else ("✗ 仅靠前置" if len(hit) == 1 else "✗ 无")
    print("%-16s %6d  %-8s %s" % (name, len(hit), flag, " / ".join(hit[:5])))
