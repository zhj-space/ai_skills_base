import io, os, re

KB = r"D:/workspace/ai_kb_base/second-brain"
CD = os.path.join(KB, "wiki", "concepts")
DD = os.path.join(KB, "wiki", "summaries")

ADD = {
    "2026-11-06-总线矩阵架构设计": ["业务过程", "数据集市"],
    "2026-11-06-sqlserver查表与字段注释": ["SQL运维"],
    "2026-11-06-数据仓库的三层境界": ["数据集市"],
    "2026-11-06-Kimball 维度建模：事实与维度": ["星型模型与雪花模型"],
}


def read(p):
    return io.open(p, encoding="utf-8").read()


def set_sec(path, text):
    s = read(path)
    head, rest = s.split("## 涉及概念", 1)
    tail = rest.split("\n## ", 1)
    after = "\n## " + tail[1] if len(tail) > 1 else ""
    io.open(path, "w", encoding="utf-8", newline="").write(
        head + "## 涉及概念\n\n" + text + "\n" + after)


for stem, adds in ADD.items():
    p = os.path.join(DD, stem + ".md")
    s = read(p)
    seg = s.split("## 涉及概念", 1)[1].split("\n## ", 1)[0]
    old = [x for x in re.findall(r"\[\[([^\]|#]+)", seg)]
    new = old + [a for a in adds if a not in old]
    line = " · ".join("[[%s]]" % x for x in new)
    set_sec(p, line)
    print("OK  %-42s %d -> %d 条" % (stem[:42], len(old), len(new)))
