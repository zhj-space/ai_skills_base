# -*- coding: utf-8 -*-
"""
check_coverage.py — 用「逐行保留率」验证整理是否全面，不靠感觉。

用法：
    python check_coverage.py <原文.md> <页面1.md> [页面2.md ...]

判据：
    原文按行拆开（跳过标题、空行、frontmatter、过短行），
    剥掉空白后逐行检查是否出现在给定页面的并集里。
    输出保留率与缺失行样例。

为什么需要它：
    2026-11-07 整理同济版高数时，前两轮都自以为「已覆盖」，
    实际定义、公式、定理、题型大量丢失。跑这个脚本才发现保留率不足。
    页面数量、断言条数都不能证明「全面」，只有逐行保留率能。
"""
import io, os, re, sys


def flat(s):
    """归一化：去掉知识点编号标记与空白，只比内容本身。

    整理时会给知识点加编号（如 `3.2-P1`、`1.1-U2`），它是元数据不是内容，
    比对前必须剥离，否则会被误判为缺失。
    """
    s = re.sub(r"`[0-9]+\.[0-9]+-[PDU]\d+`", "", s)
    s = re.sub(r"[`*]", "", s)
    return re.sub(r"\s+", "", s)


def body_lines(path):
    """取原文正文行，去掉 frontmatter、标题与空行"""
    txt = io.open(path, encoding="utf-8").read()
    # 去掉 frontmatter
    if txt.startswith("---"):
        m = re.match(r"^---\n.*?\n---\n", txt, re.S)
        if m:
            txt = txt[m.end():]
    out = []
    for ln in txt.split("\n"):
        t = ln.strip()
        if not t or t.startswith("#"):
            continue
        out.append(t)
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    pages = sys.argv[2:]
    for p in [src] + pages:
        if not os.path.exists(p):
            print("文件不存在：%s" % p)
            sys.exit(1)

    hay = flat("".join(io.open(p, encoding="utf-8").read() for p in pages))

    total = missing = 0
    structural = 0
    samples = []
    for ln in body_lines(src):
        f = flat(ln)
        if len(f) < 6:      # 过短的行（单个符号、页码）不参与判定
            continue
        total += 1
        if f not in hay:
            # 去掉标点后很短的行多为结构标记（「定义 · 是什么」「本章串联」等）
            core = re.sub(r"[\W_]+", "", f)
            if len(core) < 12:
                structural += 1
                continue
            missing += 1
            if len(samples) < 15:
                samples.append(ln[:70])

    print("原文：%s" % src)
    print("对照页面：%d 个" % len(pages))
    print("")
    print("参与判定行数：%d" % total)
    print("其中结构标记行（不计入缺失）：%d" % structural)
    print("实质内容未保留行数：%d" % missing)
    if total:
        print("实质内容保留率：%.2f%%" % ((total - structural - missing) * 100.0 / (total - structural) if total > structural else 100.0))
    if samples:
        print("\n实质缺失样例（前 %d 条）：" % len(samples))
        for s in samples:
            print("   " + s)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
