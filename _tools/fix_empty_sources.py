# -*- coding: utf-8 -*-
"""修正空壳原文的 content_status 标注。

背景：10 篇从有道云导出的笔记正文完全为空（只有 frontmatter + 标题），
但 content_status 被标成 ok，导致周检看不见这批缺口。

判定：去掉 frontmatter 和标题行后，剩余可见字符 < 10 个即视为空壳。
改动只碰 frontmatter 的元数据，不动正文，并留 content_status_note 说明。
"""
import re
from pathlib import Path

RAW = Path(r"D:/workspace/ai_kb_base/second-brain/raw")
FM = re.compile(r"^---\n.*?\n---\n", re.S)
TITLE = re.compile(r"^#.*$", re.M)


def is_empty(text: str) -> bool:
    body = FM.sub("", text)
    body = TITLE.sub("", body)
    body = re.sub(r"\s", "", body)
    return len(body) < 10


changed, skipped = [], []
for p in sorted(RAW.rglob("*.md")):
    text = p.read_bytes().decode("utf-8", "replace")
    if not is_empty(text):
        continue
    cur = re.search(r"^content_status:\s*(\S+)", text, re.M)
    if cur and cur.group(1) == "empty":
        skipped.append(p.name)
        continue
    new = re.sub(r"^content_status:\s*\S+.*$",
                 "content_status: empty\ncontent_status_note: 有道云导出时正文为空，2026-11-09 修正标注",
                 text, count=1, flags=re.M)
    if new != text:
        p.write_bytes(new.encode("utf-8"))
        changed.append(p.name)

print(f"修正 {len(changed)} 篇：")
for n in changed:
    print("  ", n)
if skipped:
    print(f"\n已是 empty，跳过 {len(skipped)} 篇")
