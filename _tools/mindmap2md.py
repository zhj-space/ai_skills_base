# -*- coding: utf-8 -*-
"""把有道 .mindmap(JSON) 转成层级 Markdown 大纲"""
import os, io, json

BASE = r"D:/workspace/ai_kb_base/_ynote_export"

def conv(p):
    d = json.load(io.open(p, encoding="utf-8"))
    nodes = d.get("nodes", [])
    if not nodes:
        return None
    by_id = {n.get("id"): n for n in nodes}
    children = {}
    root = None
    for n in nodes:
        pid = n.get("parentid")
        if n.get("isroot") or pid is None:
            root = n
        else:
            children.setdefault(pid, []).append(n)
    if root is None:
        root = nodes[0]

    lines = ["# %s" % root.get("topic", "").strip(), ""]

    def walk(node, depth):
        for c in children.get(node.get("id"), []):
            t = (c.get("topic") or "").strip().replace("\n", " ")
            if not t:
                continue
            lines.append("%s- %s" % ("  " * depth, t))
            walk(c, depth + 1)

    walk(root, 0)
    return "\n".join(lines) + "\n"

n_ok = 0
for root, _, fs in os.walk(BASE):
    for fn in fs:
        if not fn.endswith(".mindmap"):
            continue
        p = os.path.join(root, fn)
        try:
            md = conv(p)
        except Exception as e:
            print("[ERR] %s -> %s" % (fn, e))
            continue
        if not md:
            print("[SKIP] %s 无节点" % fn)
            continue
        outp = os.path.splitext(p)[0] + ".md"
        io.open(outp, "w", encoding="utf-8", newline="").write(md)
        print("[OK] %-30s %d 字" % (fn, len(md)))
        n_ok += 1
print("\n转出 %d 个 mindmap" % n_ok)
