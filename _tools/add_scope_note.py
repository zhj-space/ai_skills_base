#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""给共用概念页的「本章核心知识点」表补一行口径注（已注过的跳过）"""
import os
import re

CONCEPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'second-brain', 'wiki', 'concepts'))
PAGES = ['计算机系统知识', '计算机网络', '程序设计语言', '数据结构与算法', '信息安全',
         '知识产权与标准化', '软件工程与项目管理', '专业英语', '软考数字类考点',
         '软考考前速览', '软考高频公式速查']
NOTE = ('> 本表按软件设计师章节号编排。数据库系统工程师对应章节的逐字大纲见 '
        '[[2026-11-08-数据库系统工程师备考完整笔记]] 的原文全文段。')

for p in PAGES:
    path = os.path.join(CONCEPTS, p + '.md')
    with open(path, encoding='utf-8') as f:
        t = f.read()
    if '本表按软件设计师章节号编排' in t or '本表为软件设计师口径' in t:
        print('SKIP 已有注:', p)
        continue
    m = re.search(r'(## 本章核心知识点\n)(.*?)(?=\n## |\Z)', t, re.S)
    if not m:
        print('NO TABLE', p)
        continue
    body = m.group(2).rstrip('\n')
    new = m.group(1) + body + '\n\n' + NOTE + '\n'
    t = t[:m.start()] + new + t[m.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(t)
    print('ADDED note:', p)
