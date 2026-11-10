#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
把概念页里的「知识本体（原文全文）」段抽出来，回迁到对应文档页。
概念页只保留：frontmatter + 标题 + 一句话 + 本章核心知识点 + 七段骨架。

用法：
  python split_body.py --dry      # 只分析，不写文件
  python split_body.py --apply    # 执行
"""
import os
import re
import sys
import json

KB = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'second-brain'))
CONCEPTS = os.path.join(KB, 'wiki', 'concepts')
SUMMARIES = os.path.join(KB, 'wiki', 'summaries')

DOC_SS = '2026-11-08-软件设计师备考完整笔记.md'
DOC_DB = '2026-11-08-数据库系统工程师备考完整笔记.md'

PAGES = [
    '专业英语', '信息安全', '操作系统', '数据库系统', '数据结构与算法',
    '知识产权与标准化', '程序设计语言', '计算机系统知识', '计算机网络',
    '软件工程与项目管理', '软考下午题答题方法', '软考数字类考点', '软考考前速览',
    # 第二批：单段本体页
    'SQL语言', '关系数据库理论', '数据库新技术', '数据库运行管理与维护',
    '数据库系统工程师考试', '多媒体基础', '软件设计师考试', '软考高频公式速查',
    '面向对象技术与UML',
]

# 单段页的显式归属（段标题里不含考试名，必须靠页名判）
FORCE_OWNER = {
    'SQL语言': 'db',
    '关系数据库理论': 'db',
    '数据库新技术': 'db',
    '数据库运行管理与维护': 'db',
    '数据库系统工程师考试': 'db',
    '多媒体基础': 'ss',
    '软件设计师考试': 'ss',
    '软考高频公式速查': 'ss',
    '面向对象技术与UML': 'ss',
}

# 七段骨架的固定段名（允许包含关系）
SKELETON = ['是什么', '怎样理解', '有什么性质', '怎么用', '关系', '常见误区', '出处']
EXTRA_OK = ['本章核心知识点', '本章知识点索引']


def is_body(head):
    return '知识本体' in head


def owner(head):
    """判归属：段标题含「数据库系统工程师」→ DB，否则 → 软件设计师"""
    return 'db' if '数据库系统工程师' in head else 'ss'


def split_sections(lines):
    """按 ^## 切段，返回 [(head_or_None, [lines])]，首段 head=None"""
    secs = []
    cur_head = None
    cur = []
    for ln in lines:
        if ln.startswith('## '):
            secs.append((cur_head, cur))
            cur_head = ln[3:].strip()
            cur = []
        else:
            cur.append(ln)
    secs.append((cur_head, cur))
    return secs


def split_fm(text):
    """拆 frontmatter 与正文"""
    if not text.startswith('---'):
        return '', text
    idx = text.find('\n---', 3)
    if idx < 0:
        return '', text
    end = text.find('\n', idx + 4)
    if end < 0:
        end = len(text)
    return text[:end + 1], text[end + 1:]


def build_kp_table(body_text, exam_label):
    """从本体段正文里抽取节标题 + 首层要点，生成知识点表"""
    rows = []
    cur_sec = None
    for ln in body_text.splitlines():
        m = re.match(r'^(#{3,6})\s+(.+)$', ln)
        if m:
            cur_sec = m.group(2).strip()
            continue
        m2 = re.match(r'^- \[ \]\s+(.+)$', ln.strip()) or re.match(r'^-\s+(.+)$', ln.strip())
        if m2 and cur_sec:
            item = m2.group(1).strip()
            item = re.sub(r'\*\*', '', item)
            item = re.split(r'[：:（(]', item)[0].strip()
            if 2 <= len(item) <= 30:
                rows.append((cur_sec, item))
    # 去重、每节最多 6 条
    seen = set()
    out = []
    cnt = {}
    for sec, item in rows:
        k = (sec, item)
        if k in seen:
            continue
        seen.add(k)
        cnt[sec] = cnt.get(sec, 0) + 1
        if cnt[sec] > 6:
            continue
        out.append((sec, item))
    if not out:
        return ''
    buf = ['## 本章核心知识点', '', '| 节 | 知识点 |', '|---|---|']
    for sec, item in out:
        buf.append('| %s | %s |' % (sec.replace('|', '/'), item.replace('|', '/')))
    buf.append('')
    return '\n'.join(buf)


def main():
    apply_mode = '--apply' in sys.argv
    report = {}
    ss_parts = []
    db_parts = []

    only = None
    if '--only' in sys.argv:
        i = sys.argv.index('--only')
        if i + 1 < len(sys.argv):
            only = sys.argv[i + 1]
            apply_mode = True

    for name in PAGES:
        if only and name != only:
            continue
        path = os.path.join(CONCEPTS, name + '.md')
        if not os.path.exists(path):
            print('MISS', name)
            continue
        with open(path, encoding='utf-8') as f:
            text = f.read()
        fm, body = split_fm(text)
        lines = body.splitlines()
        secs = split_sections(lines)

        kept = []        # (head, lines)
        bodies = {'ss': [], 'db': []}
        n_body = 0
        for head, ls in secs:
            if head is not None and is_body(head):
                n_body += 1
                who = FORCE_OWNER.get(name) or owner(head)
                bodies[who].append((head, ls))
            else:
                kept.append((head, ls))

        # 若已有「本章核心知识点」保留；否则从 ss 本体段生成
        has_kp = any(h and '核心知识点' in h for h, _ in kept)
        gen_kp = ''
        if not has_kp:
            print('WARN 缺核心知识点表:', name)

        # 重建概念页
        out = [fm.rstrip('\n'), '']
        for head, ls in kept:
            if head is None:
                out.extend(ls)
            else:
                out.append('## ' + head)
                out.extend(ls)
        if gen_kp:
            # 插到「## 是什么」之前
            txt = '\n'.join(out)
            marker = '\n## 是什么'
            if marker in txt:
                txt = txt.replace(marker, '\n' + gen_kp + marker, 1)
            else:
                txt = txt + '\n' + gen_kp
            out = txt.split('\n')

        new_text = '\n'.join(out)
        new_text = re.sub(r'\n{4,}', '\n\n\n', new_text)
        if not new_text.endswith('\n'):
            new_text += '\n'

        # 收集本体段全文
        for exam in ('ss', 'db'):
            for head, ls in bodies[exam]:
                chunk = '### %s · %s\n\n' % (name, head.replace('知识本体', '').strip() or '原文')
                chunk += '\n'.join(ls).strip('\n') + '\n'
                (ss_parts if exam == 'ss' else db_parts).append(chunk)

        report[name] = {
            'old_lines': len(text.splitlines()),
            'new_lines': len(new_text.splitlines()),
            'body_sections': n_body,
            'ss_chunks': len(bodies['ss']),
            'db_chunks': len(bodies['db']),
            'gen_kp': bool(gen_kp),
            'has_kp_kept': has_kp,
        }
        if apply_mode:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print('\nss chunks: %d  db chunks: %d' % (len(ss_parts), len(db_parts)))
    print('ss chars: %d  db chars: %d' % (sum(len(x) for x in ss_parts), sum(len(x) for x in db_parts)))

    if apply_mode and not only:
        for docfile, parts, label in (
                (DOC_SS, ss_parts, '软件设计师'),
                (DOC_DB, db_parts, '数据库系统工程师')):
            p = os.path.join(SUMMARIES, docfile)
            with open(p, encoding='utf-8') as f:
                d = f.read()
            if '## 原文全文 · 逐字保留' in d:
                block = '\n'.join(parts)
                d = d.rstrip('\n') + '\n' + block
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(d)
                print('APPENDED more body to', docfile, len(block), 'chars')
                continue
            block = '\n## 原文全文 · 逐字保留\n\n> 以下为原文按章节切分的逐字内容，从原概念页回迁。章级提炼见对应概念页；此处只做证据层，供逐字核对。\n\n'
            block += '\n'.join(parts)
            d = d.rstrip('\n') + '\n' + block
            with open(p, 'w', encoding='utf-8') as f:
                f.write(d)
            print('APPENDED body to', docfile, len(block), 'chars')


if __name__ == '__main__':
    main()
