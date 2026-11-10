#!/usr/bin/env python3
"""export_ynote.py — 从有道云笔记批量导出到 llm-wiki 的 raw/docs/

用法:
    python export_ynote.py --vault "D:\\知识库\\second-brain"
    python export_ynote.py --vault <库> --gap 3 --resume

设计要点（都是踩过坑换来的）:
  1. 名录与正文分两步：先递归列全树，再逐篇读。避免边遍历边读时被配额踢断
  2. 节流: 默认每篇间隔 3 秒（约 20 次/分钟），有道服务端约 25 次/分钟就会踢人
  3. 可续传: 目标文件已存在且 content_status 非 unavailable 就跳过
  4. 读不出的标 unavailable 并写明原因 —— 绝不用猜测填补
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

CLI = Path.home() / "Tools" / "youdaonote" / "windows-x64" / "youdaonote.exe"

# 文件名里不能出现的字符（Windows）
BAD_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]')
# read 失败时 CLI 会把错误信息当正文吐出来
ERR_MARKERS = ("获取笔记内容失败", "session not found", "Request timed out", "ERROR")


def run(args, timeout=60):
    """调 CLI，返回 (stdout, ok)。"""
    try:
        r = subprocess.run(
            [str(CLI)] + args,
            capture_output=True, encoding="utf-8", errors="ignore", timeout=timeout,
        )
        return (r.stdout or "").strip(), r.returncode == 0
    except subprocess.TimeoutExpired:
        return "", False
    except Exception as e:
        return str(e), False


def list_children(folder_id):
    """列一个文件夹的直接子项，处理分页。返回 [(kind, id, name)]，kind = dir|note。"""
    items, last_id, guard = [], "", 0
    while guard < 200:
        guard += 1
        args = ["list", "-f", folder_id]
        if last_id:
            args += ["-l", last_id]
        out, ok = run(args)
        if not ok or not out:
            break
        page = []
        for line in out.splitlines():
            line = line.rstrip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            head, name = parts[0], parts[1].strip()
            m = re.match(r"^(\S+)\s+(\S+)$", head)
            if not m:
                continue
            marker, fid = m.group(1), m.group(2)
            kind = "dir" if marker.startswith("📁") else "note"
            page.append((kind, fid, name))
        if not page:
            break
        items.extend(page)
        new_last = page[-1][1]
        if new_last == last_id:      # 没有前进，说明到底了
            break
        last_id = new_last
        if len(page) < 20:           # 不满一页，通常到底
            break
        time.sleep(1)
    return items


def walk(folder_id="0", prefix="", depth=0, sink=None):
    """递归遍历，把 (相对目录, note_id, 名字) 收进 sink。"""
    if depth > 6:
        return
    for kind, fid, name in list_children(folder_id):
        if kind == "dir":
            walk(fid, f"{prefix}/{name}" if prefix else name, depth + 1, sink)
        else:
            sink.append((prefix, fid, name))


def safe(name: str) -> str:
    s = BAD_CHARS.sub("", name).strip().strip(".")
    return s or "无标题"


def read_note(note_id):
    """读一篇。返回 (正文, 失败原因或 None)。"""
    out, ok = run(["read", note_id], timeout=90)
    if not ok and not out:
        return "", "CLI 调用失败"
    if not out:
        return "", "返回空内容"
    for mk in ERR_MARKERS:
        if mk in out[:300]:
            return "", out.splitlines()[0][:120]
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--gap", type=float, default=3.0, help="每篇间隔秒数，默认 3")
    ap.add_argument("--resume", action="store_true", help="跳过已导出且可读的")
    ap.add_argument("--limit", type=int, default=0, help="只导前 N 篇，用于试跑")
    ap.add_argument("--list-only", action="store_true", help="只递归列树并缓存，不读正文")
    ap.add_argument("--use-cache", action="store_true", help="复用已缓存的目录树")
    a = ap.parse_args()

    if not CLI.exists():
        sys.exit(f"找不到有道云 CLI: {CLI}")

    vault = Path(a.vault)
    dest_root = vault / "sources" / "文档"
    dest_root.mkdir(parents=True, exist_ok=True)

    print("[1/3] 递归列目录树 …", flush=True)
    cache = vault.parent / "_ynote_tree.json"
    if a.use_cache and cache.exists():
        tree = [tuple(x) for x in json.loads(cache.read_text(encoding="utf-8"))]
        print(f"      复用缓存的目录树：{len(tree)} 篇\n", flush=True)
    else:
        tree = []
        walk("0", "", 0, tree)
        cache.write_text(json.dumps(tree, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"      共 {len(tree)} 篇笔记（已缓存到 {cache.name}）\n", flush=True)

    if a.list_only:
        print("      只列树，退出。")
        return

    if a.limit:
        tree = tree[: a.limit]
        print(f"      试跑模式：只处理前 {len(tree)} 篇\n")

    print(f"[2/3] 逐篇读取（间隔 {a.gap}s，约需 {len(tree) * a.gap / 60:.0f} 分钟）…")
    stats = {"ok": 0, "unavailable": 0, "skipped": 0}
    rows = []
    for i, (folder, note_id, name) in enumerate(tree, 1):
        base = safe(Path(name).stem)
        target_dir = dest_root / folder.strip("/") if folder else dest_root
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{base}.md"

        # 同目录重名消歧
        n = 2
        while target.exists() and a.resume:
            prev = target.read_text(encoding="utf-8", errors="ignore")
            if "content_status: ok" in prev:
                stats["skipped"] += 1
                break
            n += 1
            target = target_dir / f"{base}({n}).md"
        else:
            n = 2
            while target.exists():
                target = target_dir / f"{base}({n}).md"
                n += 1

        if a.resume and target.exists() and "content_status: ok" in target.read_text(encoding="utf-8", errors="ignore"):
            if i % 20 == 0:
                print(f"      {i}/{len(tree)}  跳过已导出的")
            continue

        body, err = read_note(note_id)
        status = "ok" if body else "unavailable"
        stats[status] += 1

        fm = [
            "---",
            f"note_id: {note_id}",
            f"title: {base}",
            f"notebook: {folder or '/'}",
            "source_type: youdao",
            "modality: text",
            f"captured_at: {date.today().isoformat()}",
            f"content_status: {status}",
            f"confidence: {0.95 if status == 'ok' else 0.0}",
            f"word_count: {len(body)}",
        ]
        if err:
            fm.append(f"loss_notes: {err}")
        fm += ["---", "", f"# {base}", ""]
        target.write_text("\n".join(fm) + ("\n" + body if body else ""), encoding="utf-8")

        rows.append({"folder": folder, "note_id": note_id, "title": base,
                     "status": status, "len": len(body), "path": str(target)})

        if i % 10 == 0 or i == len(tree):
            print(f"      {i}/{len(tree)}  ok={stats['ok']} 读不出={stats['unavailable']} 跳过={stats['skipped']}")
        if i < len(tree):
            time.sleep(a.gap)

    print("\n[3/3] 写清单 …")
    manifest = vault.parent / "_ynote_manifest.json"
    manifest.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"      {manifest}")

    print(f"\n完成：共 {len(tree)} 篇 · 可读 {stats['ok']} · 读不出 {stats['unavailable']} · 跳过 {stats['skipped']}")


if __name__ == "__main__":
    main()
