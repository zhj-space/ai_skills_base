# -*- coding: utf-8 -*-
"""共用：区分「知识点」与「章末总结」

原文每章末尾有一段串联/小结（"本章串联"、CH N、全章概括），
它属于章级导读，不是知识点，不应计入知识点编号。
"""
import re

CHAP_TAIL = re.compile(
    r"本章串联|^CH\s*\d|全章只有|全章的逻辑|用一句话概括|这一章本质|"
    r"做题前先问|把四个公式并排|它们全是同一句话|两条线："
)

def is_chap_tail(line):
    flat = re.sub(r"\*\*|\*", "", line.strip())
    return bool(CHAP_TAIL.search(flat))

def split_body(lines):
    """把一段原文行拆成 (知识点行, 章末总结行)"""
    pts, tails = [], []
    for x in lines:
        (tails if is_chap_tail(x) else pts).append(x)
    return pts, tails
