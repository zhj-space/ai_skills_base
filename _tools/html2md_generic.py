# -*- coding: utf-8 -*-
"""通用 HTML → Markdown（面向结构化讲解文章：标题/段落/列表/表格/粗体/公式）"""
import os, re, io, sys, html


def strip_noise(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S | re.I)
    s = re.sub(r"<head[^>]*>.*?</head>", "", s, flags=re.S | re.I)
    return s


def conv_table(m):
    inner = m.group(0) if hasattr(m, "group") else m
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", inner, re.S | re.I)
    out = []
    for i, r in enumerate(rows):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S | re.I)
        vals = []
        for c in cells:
            c = re.sub(r"<br\s*/?>", " ", c, flags=re.I)
            c = re.sub(r"<[^>]+>", "", c)
            c = html.unescape(c).replace("|", "\\|")
            vals.append(re.sub(r"\s+", " ", c).strip())
        if not vals:
            continue
        out.append("| " + " | ".join(vals) + " |")
        if i == 0:
            out.append("| " + " | ".join(["---"] * len(vals)) + " |")
    return "\n\n" + "\n".join(out) + "\n\n"


def convert(s):
    s = strip_noise(s)
    s = re.sub(r"<table[^>]*>.*?</table>", conv_table, s, flags=re.S | re.I)

    # 行内强调
    s = re.sub(r"</?(strong|b)[^>]*>", "**", s, flags=re.I)
    s = re.sub(r"</?(em|i)[^>]*>", "*", s, flags=re.I)

    # 公式：span.f 保留文本，用反引号包住
    s = re.sub(r'<span[^>]*class="[^"]*\bf\b[^"]*"[^>]*>(.*?)</span>',
               lambda m: "`" + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "`",
               s, flags=re.S | re.I)

    # 标题
    for n in range(1, 5):
        s = re.sub(r"<h%d[^>]*>(.*?)</h%d>" % (n, n),
                   lambda m, n=n: "\n\n" + "#" * n + " " +
                   re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n\n",
                   s, flags=re.S | re.I)

    # 列表
    s = re.sub(r"<li[^>]*>(.*?)</li>",
               lambda m: "\n- " + re.sub(r"<[^>]+>", "", m.group(1)).strip(),
               s, flags=re.S | re.I)
    s = re.sub(r"</?(ul|ol)[^>]*>", "\n", s, flags=re.I)

    # 段落与换行
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p>", "\n\n", s, flags=re.I)
    s = re.sub(r"</div>", "\n\n", s, flags=re.I)

    # 去剩余标签
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)

    # 规整空白
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    lines = []
    for ln in s.split("\n"):
        ln = ln.strip()
        # 修掉落单的加粗标记（原文标签不闭合导致）
        if ln.count("**") == 1:
            ln = ln.replace("**", "")
        lines.append(ln)
    return "\n".join(lines).strip()


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    raw = io.open(src, encoding="utf-8", errors="ignore").read()
    md = convert(raw)
    io.open(dst, "w", encoding="utf-8", newline="").write(md + "\n")
    print("转换完成：%d 字符 → %d 行" % (len(raw), md.count("\n") + 1))
