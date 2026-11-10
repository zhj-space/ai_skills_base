"""检测 raw 层变化，定位受影响的文档页。

背景：文档页只记录 compiled_at（日期），没有内容指纹，所以 raw 改了系统感知不到，
只有主动跑 check_claims 才会发现断言批量失效。

做法：给每个文档页写入 raw_hash（原文 sha256 前 12 位），之后比对即可。

用法：
  python recompile.py --init       首次初始化，给所有文档页补 raw_hash
  python recompile.py              检测：列出已变 / 已丢 / 无指纹 / 新原文
  python recompile.py --verify     检测后，自动对受影响页跑断言校验
"""
import hashlib
import io
import os
import re
import subprocess
import sys

KB = r"D:/workspace/ai_kb_base/second-brain"
DOC = os.path.join(KB, "wiki", "summaries")
RAW = os.path.join(KB, "raw")
TOOLS = os.path.dirname(os.path.abspath(__file__))

SP = re.compile(r"^source_path:[ \t]*(.+)$", re.M)
RH = re.compile(r"^raw_hash:[ \t]*(\S+)[ \t]*$", re.M)
CA = re.compile(r"^(compiled_at:[^\n]*)$", re.M)


def digest(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def scan():
    """返回 [(文档页名, 绝对路径, source_path, 现有 hash, 当前 hash 或 None)]"""
    out = []
    for f in sorted(os.listdir(DOC)):
        if not f.endswith(".md"):
            continue
        p = os.path.join(DOC, f)
        s = io.open(p, encoding="utf-8").read()
        m = SP.search(s)
        if not m:
            out.append((f[:-3], p, "", "", None))
            continue
        sp = m.group(1).strip().strip('"').replace("\\", "/")
        ap = os.path.join(KB, sp)
        cur = digest(ap) if os.path.exists(ap) else None
        hm = RH.search(s)
        out.append((f[:-3], p, sp, hm.group(1) if hm else "", cur))
    return out


def do_init():
    n = ok = 0
    for name, p, sp, old, cur in scan():
        if not sp or cur is None:
            continue
        n += 1
        if old == cur:
            continue
        s = io.open(p, encoding="utf-8").read()
        if RH.search(s):
            s = RH.sub("raw_hash: " + cur, s, count=1)
        else:
            m = CA.search(s)
            if m:
                s = s[:m.end()] + "\nraw_hash: " + cur + s[m.end():]
            else:
                s = s.replace("---\n\n# ", "---\nraw_hash: " + cur + "\n\n# ", 1)
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        ok += 1
    print("初始化完成：%d 篇有原文，写入 %d 篇的 raw_hash" % (n, ok))


def do_report(verify=False):
    rows = scan()
    changed, lost, nohash, nh_sp = [], [], [], []
    for name, p, sp, old, cur in rows:
        if not sp:
            nh_sp.append(name)
            continue
        if cur is None:
            lost.append((name, sp))
        elif not old:
            nohash.append(name)
        elif old != cur:
            changed.append((name, sp, old, cur))

    print("=== raw 变化检测 ===")
    print("文档页 %d 篇" % len(rows))
    print("  已变 %d · 原文丢失 %d · 无指纹 %d · 无 source_path %d"
          % (len(changed), len(lost), len(nohash), len(nh_sp)))
    print()

    if changed:
        print("【%d 篇原文被改动，需重编译】" % len(changed))
        for name, sp, old, cur in changed:
            print("  %-44s %s" % (name[:42], sp))
            print("      指纹 %s → %s" % (old, cur))
        print()
    if lost:
        print("【%d 篇原文已不存在】" % len(lost))
        for name, sp in lost:
            print("  %-44s %s" % (name[:42], sp))
        print()
    if nohash:
        print("【%d 篇无指纹】跑 --init 补上" % len(nohash))
        for n in nohash[:6]:
            print("  " + n)
        if len(nohash) > 6:
            print("  …另有 %d 篇" % (len(nohash) - 6))
        print()
    if nh_sp:
        print("【%d 篇无 source_path（凭据屏蔽页等）】" % len(nh_sp))

    if verify and changed:
        print("\n=== 对已变页跑断言校验 ===")
        for name, sp, _, _ in changed:
            p = os.path.join(DOC, name + ".md")
            r = subprocess.run([sys.executable, "check_claims.py", p],
                               cwd=TOOLS, capture_output=True, text=True, encoding="utf-8")
            line = [l for l in (r.stdout or "").strip().split("\n") if "合计" in l]
            print("  %-44s %s" % (name[:42], line[-1] if line else "(无输出)"))

    if not (changed or lost):
        print("没有原文变化。")
    return changed


if __name__ == "__main__":
    if "--init" in sys.argv:
        do_init()
    else:
        do_report("--verify" in sys.argv)
