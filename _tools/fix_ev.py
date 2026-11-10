# -*- coding: utf-8 -*-
"""失败的证据 -> 替换为原文中该处不含 ** 的最长连续片段"""
import io, re

SRC = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/数学/同济版高数知识点梳理.md"
raw = io.open(SRC, encoding="utf-8").read()

flat_chars, pos_map = [], []
i = 0
while i < len(raw):
    if raw.startswith("**", i):
        i += 2; continue
    ch = raw[i]
    if ch == "*":
        i += 1; continue
    if ch.isspace():
        if flat_chars and flat_chars[-1] == "\u0000":
            i += 1; continue
        flat_chars.append("\u0000"); pos_map.append(i); i += 1; continue
    flat_chars.append(ch); pos_map.append(i); i += 1
F = "".join(flat_chars)

FAILS = json_list = [
"离散的起点换成了连续的距离，逻辑结构完全不变",
"参数方程二阶导不是 ψ″/φ″",
"连续保证能取到最值",
"结论只是存在性，不告诉 ξ 在哪，也不保证唯一",
"每次使用前都要重新验证类型",
"f′ 管「往哪走",
"所以求极值要考察驻点 + 不可导点",
"逆运算不可能唯一，只能给出一个函数族",
"定积分则必须换上下限",
"它是乘积法则的逆运算",
"这一步之所以重要，是因为它证明了连续函数一定有原函数",
"它把「数不清的小块加起来」换成「看首尾两端的差",
"微元必须是线性的",
"解微分方程就是不断积分，每积一次就多一个任意常数",
"微分方程没有通用解法，所以只能分类识别、逐类攻破",
"降阶的本质是把缺的那个变量消灭，让阶数降下来",
"微分方程就退化成了代数方程",
"几何上，两个向量能产生的关系只有两种：角度和长度",
"必须有一个垂直于两者的新向量",
"本质都是凑齐这两样东西",
"却有无穷多条路径",
"要求的是所有方向都能被同一个平面近似",
"可微的充分条件",
"梯度方向就是最陡的上坡方向，梯度的模就是最大坡度",
"AC − B² = 0 时判别法失效",
"二重积分就是「这块地上方空气的体积",
"必须重新画区域重新定限，不能直接对调上下限",
"φ 是与 z 轴的夹角",
"势能的变化都一样，只取决于高度差",
"所以第二类曲面积分必须指明取哪一侧",
"它们和格林是同一句话的三个版本：内部求导 = 边界取值",
"旋度问的是「这一点是不是一个小漩涡",
"所以必须用有限来定义无限",
"所以所有正项判别法，本质上都在判断",
"交错级数靠正负抵消来收敛",
]

def flatq(s):
    s = s.replace("**", "").replace("*", "")
    return re.sub(r"\s+", "\u0000", s)

print("替换表（旧证据 -> 新证据）：\n")
rep = {}
for ev in FAILS:
    fe = flatq(ev)
    idx = F.find(fe)
    if idx < 0:
        print("!! NOTFOUND  %s" % ev); continue
    rlo = pos_map[idx]
    rhi = pos_map[min(idx + len(fe) - 1, len(pos_map)-1)] + 1
    window = raw[rlo:rhi]
    # 按 ** 切分，取最长片段
    parts = [p for p in window.split("**") if p.strip()]
    if not parts:
        print("!! EMPTY  %s" % ev); continue
    best = max(parts, key=lambda p: len(re.sub(r"\s+", "", p)))
    new = re.sub(r"\s+", "", best).strip()
    rep[ev] = new
    print("旧: %s" % ev)
    print("新: %s" % new)
    print()

io.open(r"D:/workspace/ai_kb_base/_tools/ev_replace.json", "w", encoding="utf-8", newline="") \
    .write(__import__("json").dumps(rep, ensure_ascii=False, indent=1))
print("已写 ev_replace.json（%d 条）" % len(rep))
