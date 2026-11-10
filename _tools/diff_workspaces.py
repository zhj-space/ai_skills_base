# -*- coding: utf-8 -*-
"""对比新旧工作区，找出缺失、多余与内容差异"""
import os, io, hashlib

OLD = r"D:/知识库"
NEW = r"D:/workspace/ai_kb_base"

def snap(base):
    """返回 {相对路径: (大小, md5或None)}"""
    out = {}
    for root, _, fs in os.walk(base):
        for fn in fs:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            h = None
            if fn.endswith((".md", ".py", ".json", ".txt")):
                try:
                    h = hashlib.md5(io.open(p, "rb").read()).hexdigest()
                except Exception:
                    pass
            out[rel] = (size, h)
    return out

old = snap(OLD)
new = snap(NEW)

only_old = sorted(set(old) - set(new))
only_new = sorted(set(new) - set(old))
both = sorted(set(old) & set(new))

print("旧工作区文件：%d" % len(old))
print("新工作区文件：%d" % len(new))
print()

print("【缺失】只在旧目录有：%d" % len(only_old))
for x in only_old[:30]:
    print("   %-70s %d B" % (x, old[x][0]))
if len(only_old) > 30:
    print("   ... 另有 %d 个" % (len(only_old) - 30))
print()

print("【新增】只在新目录有：%d" % len(only_new))
for x in only_new[:20]:
    print("   %-70s %d B" % (x, new[x][0]))
if len(only_new) > 20:
    print("   ... 另有 %d 个" % (len(only_new) - 20))
print()

# 内容差异
diff_size, diff_hash = [], []
for rel in both:
    so, ho = old[rel]
    sn, hn = new[rel]
    if so != sn:
        diff_size.append((rel, so, sn))
    elif ho and hn and ho != hn:
        diff_hash.append((rel, so))

print("【大小不同】%d 个" % len(diff_size))
for rel, a, b in diff_size[:15]:
    print("   %-65s %d -> %d" % (rel, a, b))
print()
print("【大小相同但内容不同】%d 个" % len(diff_hash))
for rel, s in diff_hash[:20]:
    print("   %-65s %d B" % (rel, s))
