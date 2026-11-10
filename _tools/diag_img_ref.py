# -*- coding: utf-8 -*-
"""逐字节比对 md 里的图片引用与实际文件名"""
import os, re, io, unicodedata

D = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/方法论"
md = os.path.join(D, "思维体系模型解析.md")
imgdir = os.path.join(D, "images")

s = io.open(md, encoding="utf-8").read()
refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", s)
print("md 里的引用：")
for r in refs:
    print("  repr:", repr(r))
    print("  NFC == NFD?", unicodedata.normalize("NFC", r) == unicodedata.normalize("NFD", r))
    print("  bytes:", r.encode("utf-8"))
    print("  存在?", os.path.exists(os.path.join(D, r)))
    from urllib.parse import quote, unquote
    print("  quote:", quote(r))
    print("  unquote(quote):", unquote(quote(r)))
    print("-" * 50)

print("\n实际文件名：")
for fn in sorted(os.listdir(imgdir)):
    print("  repr:", repr(fn))
    print("  存在?", os.path.exists(os.path.join(imgdir, fn)))
    print("-" * 50)

print("\n差异定位：")
files = set(os.listdir(imgdir))
for r in refs:
    base = r.split("/")[-1]
    if base not in files:
        print("  [未匹配] %r" % base)
        cand = [f for f in files if f[:20] == base[:20]]
        for c in cand:
            print("     最接近: %r" % c)
            print("     长度 %d vs %d" % (len(base), len(c)))
            for i, (a, b) in enumerate(zip(base, c)):
                if a != b:
                    print("     第 %d 位不同: %r(%U) vs %r(%U)" % (i, a, ord(a), b, ord(b)))
                    break
