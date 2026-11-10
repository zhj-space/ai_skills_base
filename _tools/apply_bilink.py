# -*- coding: utf-8 -*-
"""补齐双链：文档页「涉及概念」挂到已有概念页 + 修悬空链 + 主题地图补收。
用法：python apply_bilink.py --dry   （只打印）
      python apply_bilink.py --apply （写入）
"""
import io, os, re, sys

KB = r"D:/workspace/ai_kb_base/second-brain"
DOC = os.path.join(KB, "wiki", "summaries")
CON = os.path.join(KB, "wiki", "concepts")
APPLY = "--apply" in sys.argv

# 文档页 → 概念页（据标题归属；原页为截图，无文字可抽）
MAP = {
    # 数学 · 第 1 章（已有 极限 / 连续与间断）
    "2026-11-06-函数的极限": ["极限"],
    "2026-11-06-数列极限": ["极限"],
    "2026-11-06-无穷大无穷小的知识": ["极限"],
    "2026-11-06-无穷小的比较": ["极限"],
    "2026-11-06-极限运算": ["极限"],
    "2026-11-06-极限存在准则和两个重要极限": ["极限"],
    "2026-11-06-映射与函数": ["极限"],
    "2026-11-06-函数连续性与间断点": ["连续与间断"],
    "2026-11-06-连续函数的运算和初等函数的连续性": ["连续与间断"],
    "2026-11-06-闭区间连续函数的性质": ["连续与间断"],
    "2026-11-06-高数基本知识点": ["极限", "连续与间断"],
    # 操作系统
    "2026-11-06-linux yum命令和apt命令": ["操作系统"],
    "2026-11-06-linux 文本编辑器": ["操作系统"],
    "2026-11-06-linux 系统启动过程": ["操作系统"],
    "2026-11-06-linux历史": ["操作系统"],
    "2026-11-06-linux命令": ["操作系统"],
    "2026-11-06-linux用户和用户组管理": ["操作系统"],
    "2026-11-06-linux的学习发现": ["操作系统"],
    "2026-11-06-linux磁盘管理": ["操作系统"],
    "2026-11-06-linux系统目录结构": ["操作系统"],
    # java
    "2026-11-06-13、JSP的常用指令": ["Java"],
    "2026-11-06-16、页面间对象传递的方法": ["Java"],
    "2026-11-06-java类的重写以及重载": ["Java"],
    "2026-11-06-全局变量和局部变量": ["Java"],
    # 大数据 · dataworks 与治理规范
    "2026-11-06-数据治理": ["数据治理"],
    "2026-11-06-数据质量": ["数据治理"],
    "2026-11-06-数据安全": ["数据治理"],
    "2026-11-06-数据保护伞": ["数据治理"],
    "2026-11-06-阿里数据规范": ["OneData"],
    "2026-11-06-数据模型设计": ["维度建模", "数据建模四步"],
    "2026-11-06-划分主题域": ["主题域"],
    "2026-11-06-数据服务": ["数据中台"],
    # 架构与性能
    "2026-11-06-cpu相关指标": ["计算机体系结构"],
    "2026-11-06-计算系统性能": ["系统吞吐量"],
    "2026-11-06-阿姆达尔定律": ["流水线", "系统吞吐量"],
}

# 写了概念名但目标概念页不存在的，统一改成既有体例
NO_CONCEPT = {
    "2026-11-06-DeepSeek本地化部署": "（无独立概念页，属本地大模型部署工具链）",
    "2026-11-06-Markdown编辑器功能与快捷键": "（无独立概念页，属编辑器工具）",
    "2026-11-06-openssl加密与解密": "（无独立概念页，属 openssl 命令）",
    "2026-11-06-Python学习路线": "（无独立概念页，属学习路线导航）",
    "2026-11-06-个人能力体系构建": "（无独立概念页，属个人能力体系）",
}

# 悬空链接修正（目标不是概念页）
FIX_LINK = [
    (os.path.join(CON, "JVM.md"),
     "- 相关：[[内存管理]]",
     "- 相关：[[2026-11-06-Java内存管理-泄漏与溢出]] —— 堆内存泄漏与溢出的判别"),
    (os.path.join(CON, "垃圾回收.md"),
     "- 相关：[[内存管理]]",
     "- 相关：[[2026-11-06-Java内存管理-泄漏与溢出]] —— 堆内存泄漏与溢出的判别"),
    (os.path.join(DOC, "2026-11-06-Java内存管理-泄漏与溢出.md"),
     "[[JVM]] · [[内存管理]]",
     "[[JVM]]"),
    (os.path.join(DOC, "2026-11-06-Java类的声明与实现.md"),
     "[[Java]] · [[类与对象]]",
     "[[Java]]"),
]

MATH17 = ["极限", "连续与间断", "导数与微分", "中值定理", "泰勒公式", "不定积分",
          "定积分", "牛顿-莱布尼茨公式", "微元法", "微分方程", "向量代数",
          "偏导数与全微分", "梯度", "重积分", "曲线曲面积分",
          "格林高斯斯托克斯公式", "无穷级数"]


def set_section(path, text):
    s = io.open(path, encoding="utf-8").read()
    if "## 涉及概念" not in s:
        raise RuntimeError("无该节：" + path)
    head, rest = s.split("## 涉及概念", 1)
    tail = rest.split("\n## ", 1)
    after = "\n## " + tail[1] if len(tail) > 1 else ""
    new = head + "## 涉及概念\n\n" + text + "\n" + after
    io.open(path, "w", encoding="utf-8", newline="").write(new)


def add_section(path, text):
    s = io.open(path, encoding="utf-8").read()
    assert "## 涉及概念" not in s
    assert "\n## 出处" in s
    s = s.replace("\n## 出处", "\n## 涉及概念\n\n" + text + "\n\n## 出处", 1)
    io.open(path, "w", encoding="utf-8", newline="").write(s)


def cur_section(path):
    s = io.open(path, encoding="utf-8").read()
    if "## 涉及概念" not in s:
        return "(无该节)"
    seg = s.split("## 涉及概念", 1)[1].split("\n## ", 1)[0]
    return seg.strip()[0:40]


conset = set(f[:-3] for f in os.listdir(CON) if f.endswith(".md"))
n = 0
print("=== 一、挂到已有概念页 ===")
for stem, concepts in MAP.items():
    p = os.path.join(DOC, stem + ".md")
    if not os.path.exists(p):
        print("  !! 缺文件 %s" % stem)
        continue
    bad = [c for c in concepts if c not in conset]
    if bad:
        print("  !! 概念页不存在 %s -> %s" % (stem, bad))
        continue
    new = " · ".join("[[%s]]" % c for c in concepts)
    print("  %-40s %-16s <- %s" % (stem[:40], cur_section(p)[:14], new))
    if APPLY:
        set_section(p, new)
    n += 1

print("\n=== 二、无独立概念页（改体例，不加链）===")
for stem, text in NO_CONCEPT.items():
    p = os.path.join(DOC, stem + ".md")
    if not os.path.exists(p):
        print("  !! 缺文件 %s" % stem)
        continue
    print("  %-40s %s" % (stem[:40], text))
    if APPLY:
        set_section(p, text)
    n += 1

print("\n=== 三、补缺节：高数知识点总索引 ===")
p = os.path.join(DOC, "2026-11-07-高数知识点总索引.md")
if "## 涉及概念" in io.open(p, encoding="utf-8").read():
    print("  已有该节，跳过")
else:
    print("  增加 17 个数学概念页链接")
    if APPLY:
        add_section(p, " · ".join("[[%s]]" % c for c in MATH17))
    n += 1

print("\n=== 四、修悬空链接 ===")
for path, old, new in FIX_LINK:
    s = io.open(path, encoding="utf-8").read()
    ok = old in s
    print("  %-34s %s" % (os.path.basename(path)[:34], "改" if ok else "!! 未匹配"))
    if ok and APPLY:
        io.open(path, "w", encoding="utf-8", newline="").write(s.replace(old, new, 1))
    if ok:
        n += 1

print("\n=== 五、主题地图补收 3 个概念页 ===")
tm = os.path.join(KB, "wiki", "topic-map.md")
s = io.open(tm, encoding="utf-8").read()
edits = [
    ("### 数据库\n\n- [[pgsql]]",
     "### 数据库\n\n- [[数据库系统]] — 三级模式两层映射、ER 模型与规范化\n- [[关系代数]] — 以关系为对象的形式化查询语言，SQL 的理论基础\n- [[pgsql]]"),
    ("## 工具与应用",
     "### 思维方法\n\n- [[思维体系模型]] — 三维度、四步骤、六字口诀、一个基础\n\n## 工具与应用"),
]
for old, new in edits:
    print("  %s" % ("补" if old in s else "!! 未匹配: " + old[:20]))
    if APPLY and old in s:
        s = s.replace(old, new, 1)
if APPLY:
    io.open(tm, "w", encoding="utf-8", newline="").write(s)

print("\n%s，共 %d 项" % ("已写入" if APPLY else "dry-run 结束", n))
