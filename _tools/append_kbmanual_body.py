#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 raw 原文逐字追加到文档页的「## 原文全文 · 逐字保留」段，正文标题降级。
代码块内的行首 # 不处理（否则 bash 注释被当标题）。
"""
import os
import re

KB = r'D:/workspace/ai_kb_base/second-brain'
RAW = os.path.join(KB, 'raw/docs/personal-assets/ops/知识库搭建与运维教程.md')
DOC = os.path.join(KB, 'wiki/summaries/2026-11-09-个人知识库搭建与运维教程.md')
MARK = '## 原文全文 · 逐字保留'


def strip_fm(text):
    if not text.startswith('---'):
        return text
    i = text.find('\n---', 3)
    if i < 0:
        return text
    j = text.find('\n', i + 4)
    return text[j + 1:] if j > 0 else text


with open(RAW, encoding='utf-8') as f:
    raw = strip_fm(f.read())

out = []
in_code = False
for ln in raw.splitlines():
    if ln.strip().startswith('```'):
        in_code = not in_code
        out.append(ln)
        continue
    if not in_code:
        m = re.match(r'^(#{1,3})\s+(.*)$', ln)
        if m:
            n = len(m.group(1)) + 2
            ln = '#' * n + ' ' + m.group(2)
    out.append(ln)

body = '\n'.join(out).strip('\n')

with open(DOC, encoding='utf-8') as f:
    doc = f.read()

if MARK in doc:
    print('SKIP 已有全文段')
else:
    block = ('\n' + MARK + '\n\n'
             '> 原文逐字保留，标题统一降级以并入本段。章级提炼见 [[编译式知识库]] 与 [[知识库搭建六阶段]]。\n\n'
             + body + '\n')
    with open(DOC, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc.rstrip('\n') + '\n' + block)
    print('追加完成，正文字符:', len(body))

print('文档页行数:', len(open(DOC, encoding='utf-8').read().splitlines()))
