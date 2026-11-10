# -*- coding: utf-8 -*-
"""全库校验：双括号断链、孤岛页、图片引用、页面统计"""
import os, re, io, collections

KB = r"D:/workspace/ai_kb_base/second-brain"

def rels(base):
    out = []
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".md"):
                out.append(os.path.join(root, fn))
    return out


def strip_code(text):
    """清空代码块和行内代码，避免示例里的 [[xx]] 被当成真链接。

    顺序要紧：先吃掉围栏块，再处理行内反引号。
    否则块内的反引号会被行内规则先匹配掉，剩下的围栏就配不上对了。
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text

wiki_files = rels(os.path.join(KB, "wiki"))
src_files = rels(os.path.join(KB, "raw"))
all_md = rels(KB)

# 页面名字典（文件名去 .md）
pages = {}
for p in all_md:
    name = os.path.splitext(os.path.basename(p))[0]
    pages.setdefault(name, []).append(p)

print("全库 md：%d 篇" % len(all_md))
print("  wiki：%d 篇（概念/文档/沉淀/模板）" % len(wiki_files))
print("  sources：%d 篇" % len(src_files))

# 断链：只在 wiki 层检查 [[ ]]（模板里的占位不算）
broken = collections.Counter()
total_links = 0
outbound = collections.Counter()
inbound = collections.Counter()

for p in all_md:
    if "_templates" in p or "/raw/" in p.replace("\\", "/"):
        continue
    s = strip_code(io.open(p, encoding="utf-8").read())
    me = os.path.splitext(os.path.basename(p))[0]
    for m in re.finditer(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", s):
        tgt = m.group(1).strip()
        total_links += 1
        outbound[me] += 1
        if tgt not in pages:
            broken[tgt] += 1
        else:
            inbound[tgt] += 1

print("\nwiki 层双括号链接：%d 条" % total_links)
print("断链：%d 个目标" % len(broken))
for t, c in broken.most_common(20):
    print("   [[%s]] 被引用 %d 次" % (t, c))

# 孤岛：wiki 里无入链的页
isolated = []
for p in wiki_files:
    if "_templates" in p:
        continue
    me = os.path.splitext(os.path.basename(p))[0]
    if inbound.get(me, 0) == 0 and me not in ("主题地图", "index"):
        isolated.append(me)
SENSITIVE_MARK = "凭据已屏蔽"
sensitive = [x for x in isolated if SENSITIVE_MARK in x]
print("\n孤岛页（无入链）：%d" % len(isolated))
for x in isolated[:20]:
    print("   " + x)
if sensitive:
    print("  其中敏感隔离页（凭据类）：%d" % len(sensitive))

# 图片引用（attachments/ 从 vault 根解析）
miss_img = []
img_total = 0
for p in src_files:
    s = io.open(p, encoding="utf-8").read()
    for m in re.finditer(r"!\[[^\]]*\]\((attachments/[^)]+)\)", s):
        img_total += 1
        if not os.path.exists(os.path.join(KB, m.group(1))):
            miss_img.append((os.path.relpath(p, KB), m.group(1)))
print("\n图片引用总数：%d" % img_total)
print("图片引用缺失：%d 处" % len(miss_img))
for a, b in miss_img[:10]:
    print("   %s -> %s" % (a, b))

# sources 状态
ok = un = 0
for p in src_files:
    s = io.open(p, encoding="utf-8").read()[:400]
    if "content_status: ok" in s:
        ok += 1
    else:
        un += 1
print("\nsources 内容状态：ok %d / 非 ok %d" % (ok, un))
