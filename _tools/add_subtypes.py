"""向 ontology.json 登记两个实体子类：app_platform / numerical_tool。

按 agent.md：新增子类必须先在 entity_subtypes 登记，否则 C10 报「未登记」。
"""
import io
import json

P = r"D:/workspace/ai_kb_base/second-brain/ontology.json"

NEW = {
    "app_platform": {
        "label": "应用开发平台",
        "definition": "把界面、桥接与打包打成一体的开发环境，一套代码产出多平台应用",
    },
    "numerical_tool": {
        "label": "数值计算工具",
        "definition": "以矩阵或数组为第一等数据类型的计算环境，附带专用工具箱",
    },
}

d = json.load(io.open(P, encoding="utf-8"))
sub = d["entity_subtypes"]
added = 0
for k, v in NEW.items():
    if k in sub:
        print("已存在，跳过 %s" % k)
        continue
    sub[k] = v
    added += 1

d["updated"] = "2026-11-08"
io.open(P, "w", encoding="utf-8", newline="").write(
    json.dumps(d, ensure_ascii=False, indent=2))

print("新增子类 %d 个，当前共 %d 个：" % (added, len([k for k in sub if not k.startswith("_")])))
for k, v in sub.items():
    if not k.startswith("_"):
        print("  %-22s %s" % (k, v["label"]))
