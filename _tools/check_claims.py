# -*- coding: utf-8 -*-
"""
校验文档页的 high 断言证据是否逐字存在于原文。
用法：python check_claims.py <文档页路径> [...]
      python check_claims.py --all     # 校验 wiki/文档 全部
"""
import os, re, io, sys

KB = r"D:/workspace/ai_kb_base/second-brain"

def load_doc(p):
    s = io.open(p, encoding="utf-8").read()
    m = re.search(r"^source_path:\s*(.+)$", s, re.M)
    src = m.group(1).strip().strip('"') if m else None
    return s, src

def evidence_blocks(s):
    """抓出成对的『断言行 + 引用证据行』"""
    pairs = []
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        m = re.match(r"^- .*``\s*$", ln.strip()) or re.match(r"^- .*`(high|medium|low)`\s*$", ln.strip())
        if not m:
            continue
        conf = re.search(r"`(high|medium|low)`\s*$", ln.strip())
        conf = conf.group(1) if conf else "?"
        stmt = re.sub(r"`(high|medium|low)`\s*$", "", ln.strip())
        stmt = re.sub(r"^-\s*", "", stmt).strip()
        ev = None
        for j in range(i + 1, min(i + 4, len(lines))):
            t = lines[j].strip()
            if t.startswith(">"):
                ev = t.lstrip("> ").strip()
                break
        if ev:
            pairs.append((conf, stmt, ev))
    return pairs

def check(docp):
    s, src = load_doc(docp)
    name = os.path.basename(docp)
    if not src:
        print("[SKIP] %s 无 source_path" % name)
        return 0, 0
    srcp = os.path.join(KB, src)
    if not os.path.exists(srcp):
        print("[FAIL] %s 原文不存在：%s" % (name, src))
        return 0, 1
    raw = io.open(srcp, encoding="utf-8").read()
    # 归一化：去掉所有空白，便于比对（原文有大量空格/换行分隔）
    flat = re.sub(r"\s+", "", raw)

    pairs = evidence_blocks(s)
    ok = bad = 0
    for conf, stmt, ev in pairs:
        if conf != "high":
            continue
        # 剥掉「原文：」和中文引号
        e = ev
        e = re.sub(r"^原文[：:]\s*", "", e)
        e = e.strip("「」\"' ")
        ef = re.sub(r"\s+", "", e)
        if not ef:
            continue
        if ef in flat:
            ok += 1
        else:
            bad += 1
            print("[逐字不匹配] %s" % name)
            print("   断言: %s" % stmt[:60])
            print("   证据: %s" % e[:100])
    return ok, bad

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("用法: python check_claims.py <文档页> | --all")
        sys.exit(0)
    if args[0] == "--all":
        D = os.path.join(KB, "wiki", "summaries")
        files = [os.path.join(D, f) for f in sorted(os.listdir(D)) if f.endswith(".md")]
    else:
        files = args
    T_ok = T_bad = 0
    for f in files:
        o, b = check(f)
        T_ok += o
        T_bad += b
    print("\n合计：逐字通过 %d 条 / 不匹配 %d 条（共 %d 篇）" % (T_ok, T_bad, len(files)))
