#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_skills.py — skill 目录的链接体检（不是定时任务，手动跑）

正常状态
    llm-wiki-skills 是一个 junction，指向 .workbuddy/skills。
    两个路径是同一份物理文件，改哪边都一样，不需要同步。

异常状态
    链接被某个工具展开成了真实目录（备份软件还原、资源管理器拖拽、项目整体复制
    都会干这事）。此时两份各走各的，改一边另一边永远不变，而且没有任何提示。

用法
    python _tools/sync_skills.py            体检，看链接还在不在
    python _tools/sync_skills.py --check    体检；异常时退出码 1
    python _tools/sync_skills.py --apply    链接已断时，把生效位内容推回真源（应急）

判定一律用 sha256，不看 mtime——复制和检出都会让时间失真。
"""
import argparse
import hashlib
import os
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "llm-wiki-skills"
DST = ROOT / ".workbuddy" / "skills"

REPARSE_FLAG = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def is_link(path: Path) -> bool:
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if getattr(st, "st_file_attributes", 0) & REPARSE_FLAG:
        return True
    return stat.S_ISLNK(st.st_mode)


def real(path: Path) -> Path:
    try:
        return Path(os.path.realpath(path))
    except OSError:
        return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def scan(base: Path) -> dict:
    if not base.is_dir():
        return {}
    return {p.relative_to(base).as_posix(): p for p in sorted(base.rglob("*")) if p.is_file()}


def main() -> int:
    ap = argparse.ArgumentParser(description="skill 目录链接体检")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="异常时退出码 1")
    g.add_argument("--apply", action="store_true", help="链接已断时把生效位推回真源")
    args = ap.parse_args()

    print(f"真源    {SRC}")
    print(f"生效位  {DST}")
    print()

    if not SRC.exists():
        print("[FAIL] 真源路径不存在。链接被删了，重建：")
        print(f'    New-Item -ItemType Junction -Path "{SRC}" -Target "{DST}"')
        return 1
    if not DST.is_dir():
        print("[FAIL] 生效位不存在，系统加载不到任何 skill")
        return 1

    if is_link(SRC):
        src_real, dst_real = real(SRC), real(DST)
        if src_real == dst_real:
            n = len(scan(DST))
            print(f"[OK] 链接模式生效：两份是同一份文件（{n} 个），改哪边都一样，无需同步")
            print("     别忘了：改完要新开会话才加载。")
            return 0
        print("[FAIL] 真源是链接，但指向了别处：")
        print(f"       当前指向 {src_real}")
        print(f"       应该指向 {dst_real}")
        return 1

    print("[WARN] 链接已断：真源是独立真实目录，两份正在各走各的")
    print("       大概率是备份还原或项目复制把 junction 展开成了实体目录")
    print()

    src, dst = scan(SRC), scan(DST)
    add, upd, same = [], [], []
    for rel, sp in src.items():
        dp = dst.get(rel)
        if dp is None:
            add.append(rel)
        elif digest(sp) != digest(dp):
            upd.append(rel)
        else:
            same.append(rel)
    orphan = [r for r in dst if r not in src]

    to_src = []
    for rel in upd:
        if (DST / rel).stat().st_mtime > (SRC / rel).stat().st_mtime + 1:
            to_src.append(rel)

    print(f"       真源 {len(src)} 文件 · 生效位 {len(dst)} 文件 · 其中 {len(same)} 个相同")
    if add:
        print(f"       只在真源有：{', '.join(add)}")
    if orphan:
        print(f"       只在生效位有：{', '.join(orphan)}")
    if upd:
        print(f"       两边不同：{', '.join(upd)}")
        if to_src:
            print(f"       ↳ 其中 {', '.join(to_src)} 生效位更新，可能改在了生效位上")

    print()
    print("       正确做法是重建链接（不是同步），先把不一致的内容人工合并：")
    print(f'         Remove-Item "{SRC}" -Recurse -Force')
    print(f'         New-Item -ItemType Junction -Path "{SRC}" -Target "{DST}"')

    if args.check:
        return 1
    if not args.apply:
        return 0

    print()
    print("       按 --apply：以生效位为准，覆盖真源")
    for rel in add + upd:
        target = SRC / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DST / rel, target)
    for rel in orphan:
        (SRC / rel).unlink()
    print(f"       完成：覆盖 {len(add) + len(upd)} · 删除 {len(orphan)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
