#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把工作区根的《知识库搭建与运维教程.md》落到 raw/docs/personal-assets/ops/ 并补 frontmatter"""
import os
import shutil

SRC = r'D:/workspace/ai_kb_base/知识库搭建与运维教程.md'
DST_DIR = r'D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/ops'
DST = os.path.join(DST_DIR, '知识库搭建与运维教程.md')

with open(SRC, encoding='utf-8') as f:
    body = f.read()

lines = body.splitlines()
nonspace = [l for l in lines if l.strip()]
chars = sum(len(l) for l in lines)
words = chars // 2  # 中文粗估

fm = f'''---
title: 个人知识库搭建与运维教程
notebook: personal-assets/运维
source_type: local
modality: text
captured_at: 2026-11-09
content_status: ok
confidence: 0.95
word_count: {words}
images: 0
original: 工作区根 知识库搭建与运维教程.md（18090 字节，用户自写 md，非导出）
---
'''
os.makedirs(DST_DIR, exist_ok=True)
out = fm + body
if not out.endswith('\n'):
    out += '\n'
with open(DST, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)

print('落地:', DST)
print('字节:', os.path.getsize(DST), '行数:', len(out.splitlines()), '有效行:', len(nonspace), '估算字数:', words)
