import io
import os
import re

KB = r"D:/workspace/ai_kb_base/second-brain"
SD = os.path.join(KB, "raw")
WD = os.path.join(KB, "wiki")

txt = img = total = 0
for r, _, fs in os.walk(SD):
    for f in fs:
        if not f.endswith(".md"):
            continue
        total += 1
        p = os.path.join(r, f)
        s = io.open(p, encoding="utf-8").read()
        m = re.search(r"^modality:[ \t]*(\S+)", s, re.M)
        w = re.search(r"^word_count:[ \t]*(\d+)", s, re.M)
        is_img = (m and m.group(1) == "image") or (w and int(w.group(1)) < 60)
        if is_img:
            img += 1
        else:
            txt += 1

print("sources 总篇数 %d" % total)
print("  有正文可抽取 %d" % txt)
print("  纯图/极短（抽取无收益）%d" % img)

n_md = 0
n_img = 0
for r, _, fs in os.walk(KB):
    for f in fs:
        if f.endswith(".md"):
            n_md += 1
        elif f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            n_img += 1
print("\n全库 md %d 篇 · 图片 %d 张" % (n_md, n_img))

# 现有能力盘点
tools = sorted(f for f in os.listdir(r"D:/workspace/ai_kb_base/_tools") if f.endswith(".py"))
print("\n现有脚本 %d 个，其中校验/检索类：%s"
      % (len(tools), "、".join(t for t in tools
                              if any(k in t for k in ("check", "verify", "queue", "coverage", "audit")))[:120]))
