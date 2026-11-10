# -*- coding: utf-8 -*-
"""列出 12 篇真空笔记详情，并检查是否与库内其他篇重复"""
import os, re, io

KB = r"D:/workspace/ai_kb_base/second-brain"
SRC = os.path.join(KB, "raw", "summaries", "个人资产体系")

RE_WC = re.compile(r"^word_count:\s*(\d+)", re.M)
RE_IMG = re.compile(r"^images:\s*(\d+)", re.M)

targets = [
    "java/Maven/Apache Maven POM.md",
    "java/Maven/Apache Maven 概述.md",
    "python/入门/Python GUI编程(Tkinter).md",
    "python/入门/Python SMTP发送邮件.md",
    "python/入门/Python XML解析.md",
    "python/入门/Python 多线程.md",
    "python/入门/Python 网络编程.md",
    "python/入门/Python2.x与3\u200b\u200b.x版本区别.md",
    "前端/应用系统之间数据传递的几种方式.md",
    "大数据/etl相关/kettle/kettle相关.md",
    "系统运维/Nginx 502 Bad Gateway错误可能原因及解决方法.md",
    "自媒体发布/python的环境搭建.md",
]

# 建全库索引：文件名 -> [(相对路径, 字数)]
allmd = {}
for root, _, fs in os.walk(SRC):
    for fn in fs:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        s = io.open(p, encoding="utf-8").read()
        m = RE_WC.search(s)
        w = int(m.group(1)) if m else -1
        allmd.setdefault(fn, []).append(
            (os.path.relpath(p, SRC).replace(os.sep, "/"), w))

print("%-46s %5s %5s  %s" % ("文件", "字数", "图", "同名的其它副本"))
print("-" * 100)
for t in targets:
    p = os.path.join(SRC, t)
    if not os.path.exists(p):
        # 处理不可见字符导致的不匹配
        cand = [x for x in allmd if x.replace("\u200b", "") == os.path.basename(t).replace("\u200b", "")]
        if cand:
            p = os.path.join(SRC, cand[0])
            t = t.replace(t.split("/")[-1], cand[0])
        else:
            print("%-46s  未找到" % t)
            continue
    s = io.open(p, encoding="utf-8").read()
    mw, mi = RE_WC.search(s), RE_IMG.search(s)
    w = mw.group(1) if mw else "?"
    n = mi.group(1) if mi else "?"
    fn = os.path.basename(p)
    others = [(x, ww) for x, ww in allmd.get(fn, []) if x != t]
    note = ""
    if others:
        note = " / ".join("%s(%d字)" % (a, b) for a, b in others)
    else:
        # 找去掉数字前缀后的相似名
        base = re.sub(r"^\d+[、.\s]*", "", fn[:-3])
        for k in allmd:
            kb = re.sub(r"^\d+[、.\s]*", "", k[:-3])
            if k != fn and kb == base:
                note += " %s" % k
    print("%-46s %5s %5s  %s" % (t, w, n, note))
