# -*- coding: utf-8 -*-
"""抽检 raw 技术文档里命中的密码值属于哪一类：常见占位符 / 需人工确认。

只输出长度和类别，不打印密码本身，避免二次泄露。
"""
import re
from pathlib import Path

ROOT = Path(r"D:/workspace/ai_kb_base")

PATTERNS = [
    re.compile(r"密码\s*[是为:：]\s*([^\s，。；]{2,40})"),
    re.compile(r"(?i)password\s*[:=]\s*([^\s,;\"')]{2,40})"),
    re.compile(r"(?i)passwd\s*[:=]\s*([^\s,;\"')]{2,40})"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*([^\s,;\"')]{4,60})"),
    re.compile(r"(?i)secret\s*[:=]\s*([^\s,;\"')]{4,60})"),
]

# 公认示例值，泄露无实际危害
PLACEHOLDERS = {
    "123456", "12345678", "1234567890", "password", "passwd", "root", "admin",
    "test", "000000", "111111", "abc123", "yourpassword", "xxx", "***", "******",
    "123123", "qwerty", "sa", "postgres", "mysql", "oracle", "hive", "sqoop",
}

files = sorted((ROOT / "second-brain/raw").rglob("*.md"))
hits = []
for p in files:
    try:
        text = p.read_bytes().decode("utf-8", "replace")
    except OSError:
        continue
    for pat in PATTERNS:
        for m in pat.finditer(text):
            v = m.group(1).strip("'\"`()[]{}<>")
            if not v:
                continue
            low = v.lower()
            kind = "占位符" if low in PLACEHOLDERS else (
                "含变量" if ("{" in v or "$" in v or v.startswith("your")) else "需确认"
            )
            hits.append((kind, len(v), p.relative_to(ROOT).as_posix()))
            break

from collections import Counter
c = Counter(k for k, _, _ in hits)
print(f"共命中 {len(hits)} 处\n")
for k, n in c.most_common():
    print(f"  {k}：{n}")
print()
need = [h for h in hits if h[0] == "需确认"]
if need:
    print("需人工确认的（只给长度，不打印值）：")
    for k, ln, rel in need[:25]:
        print(f"  长度 {ln:>2}  {rel}")
    print(f"  共 {len(need)} 处")
else:
    print("没有需要人工确认的，全部是占位符或变量。")
