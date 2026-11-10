# -*- coding: utf-8 -*-
"""md5 集合比对：确认迁移后没有丢失任何一张图的内容"""
import os, hashlib, collections

BAK = r"D:/workspace/ai_kb_base/_backup_图片迁移前_20261106/sources_文档"
DOCS = r"D:/workspace/ai_kb_base/second-brain/attachments/docs"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

bak = collections.Counter()
n_bak = 0
for root, _, files in os.walk(BAK):
    if os.path.basename(root) != "images":
        continue
    for fn in files:
        bak[md5(os.path.join(root, fn))] += 1
        n_bak += 1

new = collections.Counter()
n_new = 0
for fn in os.listdir(DOCS):
    p = os.path.join(DOCS, fn)
    if os.path.isfile(p):
        new[md5(p)] += 1
        n_new += 1

print("备份图片 %d 张，唯一内容 %d 种" % (n_bak, len(bak)))
print("迁移后   %d 张，唯一内容 %d 种" % (n_new, len(new)))

missing = set(bak) - set(new)
extra = set(new) - set(bak)
print("\n备份有但迁移后没有的内容：%d 种" % len(missing))
print("迁移后有但备份没有的内容：%d 种" % len(extra))

if not missing and not extra:
    print("\n结论：内容集合完全一致，去重只删了重复副本，零内容丢失")
else:
    for h in list(missing)[:5]:
        print("  缺失 hash:", h)
