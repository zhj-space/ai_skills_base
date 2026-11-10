# -*- coding: utf-8 -*-
"""把 skill 里的示例写法改成不触发自身敏感规则的形式。

原因：`pwd：xxx` 这种示例会被 scan_sensitive 的 `pwd[:：=]\\s*(\\S{4,})` 命中，
因为 \\S{4,} 会把紧跟的反引号和中文一起吃进去，误判成真实密码。
示例本身不该触发规则，所以改写措辞。
"""
from pathlib import Path

FILES = [
    r"C:\Users\46642\.workbuddy\skills\kb-ops\SKILL.md",
    r"D:\workspace\ai_kb_base\.workbuddy\skills\kb-ops\SKILL.md",
    r"D:\workspace\ai_kb_base\llm-wiki-skills\kb-ops\SKILL.md",
]

PAIRS = [
    (
        "- `pwd：xxx`（缩写 + **中文冒号**，ASCII 冒号的规则抓不到）",
        "- `pwd` 后跟中文冒号再加明文（旧规则只认 ASCII 冒号，静默漏报）",
    ),
    (
        "- `账号：xxx@qq.com`（邮箱在账号字段里）",
        "- 账号字段里塞邮箱（「账号」加全角冒号，值是邮箱地址）",
    ),
    (
        "- `\"id\": \"uuid\"`（v2ray/vmess 配置里的 UUID，原文注明「也是密码」）",
        "- 配置里 `id` 字段放 UUID（v2ray/vmess 服务端凭据，原文注明「也是密码」）",
    ),
]

for f in FILES:
    p = Path(f)
    if not p.is_file():
        print("跳过（不存在）:", f)
        continue
    t = p.read_bytes().decode("utf-8")
    n = 0
    for old, new in PAIRS:
        if old in t:
            t = t.replace(old, new)
            n += 1
    p.write_bytes(t.encode("utf-8"))
    print(f"替换 {n} 处：{p.parent.name}")
