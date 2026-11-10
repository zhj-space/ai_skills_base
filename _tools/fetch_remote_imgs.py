# -*- coding: utf-8 -*-
"""把构建产物里残留的远程图片全部下载到本地 images/ 并改写引用"""
import os, re, io, subprocess, hashlib

BUILD = r"D:/workspace/ai_kb_base/_build_sources_文档/个人资产体系"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CNT = {"ok": 0, "fail": 0}

def dl(url, outdir):
    ext = ".png"
    m = re.search(r"\.(png|jpg|jpeg|gif|webp|svg|bmp)(\?|$)", url, re.I)
    if m:
        ext = "." + m.group(1).lower()
    name = "ext_" + hashlib.md5(url.encode("utf-8")).hexdigest()[:16] + ext
    dst = os.path.join(outdir, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return name
    try:
        subprocess.run(["curl", "-sS", "-L", "--max-time", "45", "-o", dst, "-A", UA, url],
                       check=True, capture_output=True)
        if os.path.exists(dst) and os.path.getsize(dst) > 100:
            return name
    except Exception:
        pass
    if os.path.exists(dst):
        try:
            os.remove(dst)
        except Exception:
            pass
    return None

for root, dirs, files in os.walk(BUILD):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(root, fn)
        s = io.open(p, encoding="utf-8").read()
        if "](" not in s:
            continue
        imgdir = os.path.join(root, "images")
        hits = []

        def repl(m):
            alt, url = m.group(1), m.group(2)
            if not re.search(r"\.(png|jpg|jpeg|gif|webp|svg|bmp)(\?|$)", url, re.I):
                return m.group(0)
            os.makedirs(imgdir, exist_ok=True)
            name = dl(url, imgdir)
            if name:
                CNT["ok"] += 1
                hits.append(1)
                return "![%s](images/%s)" % (alt, name)
            CNT["fail"] += 1
            return m.group(0)

        s2 = re.sub(r"!\[([^\]]*)\]\((https?://[^)]+)\)", repl, s)
        if hits:
            io.open(p, "w", encoding="utf-8", newline="").write(s2)

print("下载成功 %d / 失败 %d" % (CNT["ok"], CNT["fail"]))
