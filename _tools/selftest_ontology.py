# -*- coding: utf-8 -*-
"""本体校验器自测：在临时库中注入各类错误，确认每条约束都能抓到。

v5 语义：type 定大类（concept/entity/method/metric + doc/digest/index），
        entity_type 只作实体子类。

用法：python selftest_ontology.py
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

SRC = r"D:/workspace/ai_kb_base/second-brain/ontology.json"
HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check_ontology.py")

TPL = """---
type: {tp}
{etype_line}name: {name}
aliases: [{aliases}]
updated: 2026-11-08
---

# {name}

> 测试用。

## 是什么

测试。

## 怎么用

{steps}

## 关系

{rel}

## 出处

- 测试
"""

CASES = {
    # name: (type, entity_type, aliases, relations, how-to)
    "甲": ("concept", "", "", "- broader:[[乙]]", "1. 一步"),
    "乙": ("concept", "", "别名X",
           "- broader:[[甲]]\n- related_to:[[不存在的页]]\n- requires:[[丙]]", "1. 一步"),
    "丙": ("entity", "runtime", "别名X",
           "- requires:[[乙]]\n- produces:[[丁]]\n- 神秘关系：[[甲]]", "1. 一步"),
    "丁": ("metric", "", "", "- related_to:[[甲]]", "1. 一步"),
    "戊": ("method", "", "", "- related_to:[[甲]]", "1. 只有一步"),
    "己": ("concept", "", "", "- broader:[[丙]]", "1. 一步"),
    "庚": ("entity", "runtime", "", "- related_to:[[甲]]", "1. 一步"),
    # C10 三个用例：非实体页带 entity_type / 实体页缺子类 / 子类未登记
    "_辛": ("concept", "metric", "", "- related_to:[[甲]]", "1. 一步"),
    "_壬": ("entity", "", "", "- related_to:[[甲]]", "1. 一步"),
    "_癸": ("entity", "unknown_x", "", "- related_to:[[甲]]", "1. 一步"),
}


def build(root):
    for sub in ("wiki/concepts", "wiki/entities", "wiki/methods", "wiki/metrics",
                "wiki/summaries", "wiki/analysis"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    shutil.copy(SRC, os.path.join(root, "ontology.json"))
    for name, (tp, sub, al, rel, steps) in CASES.items():
        etype_line = ("entity_type: %s\n" % sub) if sub else ""
        p = os.path.join(root, "wiki", "concepts", name + ".md")
        io.open(p, "w", encoding="utf-8", newline="").write(
            TPL.format(tp=tp, etype_line=etype_line, name=name,
                       aliases=al, rel=rel, steps=steps))
    # D1：涉及概念为空
    io.open(os.path.join(root, "wiki", "summaries", "测试文档.md"), "w",
            encoding="utf-8", newline="").write(
        "---\ntype: doc\ntitle: 测试文档\n---\n\n# 测试文档\n\n"
        "## 涉及概念\n\n\n## 原文位置\n\n`x`\n")
    # G1：无 based_on
    io.open(os.path.join(root, "wiki", "analysis", "测试沉淀.md"), "w",
            encoding="utf-8", newline="").write(
        "---\ntype: digest\ntitle: 测试沉淀\n---\n\n# 测试沉淀\n\n正文\n")


EXPECT = {
    "C1": ["不存在"],
    "C2": ["互标"],
    "C3": ["前置环"],
    "C4": ["produces metric"],
    "C5": ["未登记关系词"],
    "C6": ["同时属于"],
    "C7": ["broader──> 丙（entity）"],
    "C8": ["未写版本"],
    "C9": ["关系段只有 related_to"],
    "C10": ["不该有 entity_type", "缺 entity_type 子类", "实体子类「unknown_x」未登记"],
    "D1": ["涉及概念为空"],
    "G1": ["无 based_on"],
}

root = tempfile.mkdtemp(prefix="onto_test_")
try:
    build(root)
    env = dict(os.environ, KB_ROOT=root)
    out = subprocess.run([sys.executable, CHECK], capture_output=True, text=True,
                         env=env, encoding="utf-8").stdout
    print(out)
    print("=== 自测结果 ===")
    ok = True
    total = 0
    for cid, kws in EXPECT.items():
        for kw in kws:
            total += 1
            hit = kw in out
            print("%s %s 期望出现「%s」" % ("PASS" if hit else "FAIL", cid, kw))
            ok = ok and hit
    print("\n%s" % ("%d/%d 约束均可触发（%d 项检查全过）"
                    % (len(EXPECT), len(EXPECT), total) if ok else "有约束未触发，需修"))
    sys.exit(0 if ok else 1)
finally:
    shutil.rmtree(root, ignore_errors=True)
