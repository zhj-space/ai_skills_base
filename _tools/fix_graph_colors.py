"""重写 Obsidian 图谱配置：目录过滤 + 按 type 上色。

用法：python fix_graph_colors.py
"""
import io
import json

P = r"D:/workspace/ai_kb_base/second-brain/.obsidian/graph.json"


def rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16) * 65536 + int(h[2:4], 16) * 256 + int(h[4:6], 16)


DIRS = [
    ("wiki/concepts", "#7F77DD", "概念"),
    ("wiki/entities", "#5DCAA5", "实体"),
    ("wiki/methods", "#F0997B", "方法"),
    ("wiki/metrics", "#EF9F27", "指标"),
    ("wiki/analysis", "#4EC9E0", "问答沉淀"),
    ("wiki/summaries", "#8B93A8", "文档证据页"),
]

QUOTE = chr(34)
groups = []
for path, color, label in DIRS:
    q = "path:" + QUOTE + path + QUOTE
    groups.append({"query": q, "color": {"a": 1, "rgb": rgb(color)}})

search = " OR ".join(g["query"] for g in groups)

d = json.load(io.open(P, encoding="utf-8"))
d["search"] = search
d["colorGroups"] = groups
d["collapse-color-groups"] = False
d["hideUnresolved"] = True
d["showOrphans"] = True
d["showAttachments"] = False
d["showTags"] = False
d["nodeSizeMultiplier"] = 1
d["linkDistance"] = 160
d["scale"] = 0.85
d["textFadeMultiplier"] = 1

io.open(P, "w", encoding="utf-8", newline="").write(
    json.dumps(d, ensure_ascii=False, indent=2))

print("已写入 %d 个颜色组：" % len(groups))
for (path, color, label), g in zip(DIRS, groups):
    print("  %-20s %-14s %s rgb=%d" % (path, label, color, g["color"]["rgb"]))
print()
print("search =")
print("  " + search)
print()
print("verify:", len(json.load(io.open(P, encoding="utf-8"))["colorGroups"]), "groups")
