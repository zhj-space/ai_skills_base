#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修正文档页「原文全文 · 逐字保留」段的小节标题：
1. 去掉页名后的重复间隔点 `· ·`
2. 段内正文标题整体降 2 级（最多 ######），避免与段标题同级
"""
import os
import re

SUMMARIES = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'second-brain', 'wiki', 'summaries'))
DOCS = ['2026-11-08-软件设计师备考完整笔记.md', '2026-11-08-数据库系统工程师备考完整笔记.md']
MARK = '## 原文全文 · 逐字保留'


def demote(line):
    m = re.match(r'^(#{1,6})\s+(.*)$', line)
    if not m:
        return line
    n = min(len(m.group(1)) + 2, 6)
    return '#' * n + ' ' + m.group(2)


for d in DOCS:
    p = os.path.join(SUMMARIES, d)
    with open(p, encoding='utf-8') as f:
        lines = f.read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(MARK))
    except StopIteration:
        print('NO MARK', d)
        continue
    out = lines[:start + 1]
    for l in lines[start + 1:]:
        if l.startswith('### ') and '· 原文全文' in l or (l.startswith('### ') and '（原文全文保留）' in l):
            l = l.replace(' · · ', ' · ').replace('· ·', '·')
        elif l.startswith('#'):
            l = demote(l)
        out.append(l)
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('fixed', d, 'from line', start + 1)
