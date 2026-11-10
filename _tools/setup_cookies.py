import json
import os
import sys

REPO = r"D:\workspace\ai_kb_base\_tools\youdaonote-pull"
SETTING = os.path.join(os.environ["APPDATA"], "ynote-desktop", "setting.json")
OUT_DIR = r"D:/workspace/ai_kb_base/_ynote_export"

# 脚本硬性要求 cookies[0] 必须是 YNOTE_CSTK，顺序不能改
ORDER = ["YNOTE_CSTK", "YNOTE_LOGIN", "YNOTE_SESS"]

cfg = json.load(open(SETTING, encoding="utf-8"))
pool = {}
for c in cfg.get("cookies", []):
    if c.get("name") in ORDER and "note.youdao.com" in c.get("domain", ""):
        pool[c["name"]] = c["value"]

missing = [n for n in ORDER if not pool.get(n)]
if missing:
    print("缺少 cookie:", ", ".join(missing))
    sys.exit(1)

rows = [[n, pool[n], ".note.youdao.com", "/"] for n in ORDER]
with open(os.path.join(REPO, "cookies.json"), "w", encoding="utf-8") as f:
    json.dump({"cookies": rows}, f, ensure_ascii=False, indent=4)

for i, (n, v, d, p) in enumerate(rows):
    print(f"  [{i}] {n}  长度{len(v)}")

conf = {"local_dir": OUT_DIR, "ydnote_dir": "", "smms_secret_token": "", "is_relative_path": True}
with open(os.path.join(REPO, "config.json"), "w", encoding="utf-8") as f:
    json.dump(conf, f, ensure_ascii=False, indent=4)

print("\n✓ cookies.json 顺序已修正（YNOTE_CSTK 在第一）")
print("✓ config.json 已写入")
