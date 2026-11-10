# -*- coding: utf-8 -*-
"""
把有道 .note（HTML 富文本）转换成 Markdown，并把图片下载到本地 images/ 目录。
用法：python note2md.py [--dry 文件名关键字] [--limit N]
"""
import os, re, io, sys, html, subprocess, hashlib, json

BASE = r"D:/workspace/ai_kb_base/_ynote_export"
COOKIE_JSON = r"D:/workspace/ai_kb_base/_tools/youdaonote-pull/cookies.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def load_cookie():
    d = json.load(io.open(COOKIE_JSON, encoding="utf-8"))
    return "; ".join("%s=%s" % (c[0], c[1]) for c in d["cookies"])

COOKIE = load_cookie()

# ---------- 图片下载 ----------
def dl_image(url, outdir):
    """下载图片，返回本地文件名；失败返回 None"""
    ext = ".png"
    m = re.search(r"\.(png|jpg|jpeg|gif|webp|bmp)$", url.split("?")[0], re.I)
    if m:
        ext = "." + m.group(1).lower()
    name = "note_" + hashlib.md5(url.encode("utf-8")).hexdigest()[:16] + ext
    dst = os.path.join(outdir, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return name
    cmd = [
        "curl", "-sS", "-L", "--max-time", "60",
        "-o", dst,
        "-H", "Cookie: " + COOKIE,
        "-H", "Referer: https://note.youdao.com/",
        "-A", UA,
        url,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(dst) and os.path.getsize(dst) > 200:
            # 校验是否为图片
            with open(dst, "rb") as f:
                head = f.read(16)
            if head[:2] == b"\x89P" or head[:3] == b"\xff\xd8\xff" or head[:4] == b"GIF8" or head[:4] == b"RIFF":
                return name
            os.remove(dst)
    except Exception:
        pass
    if os.path.exists(dst):
        try:
            os.remove(dst)
        except Exception:
            pass
    return None

# ---------- HTML -> Markdown ----------
def conv_pre(inner):
    t = re.sub(r"<br\s*/?>", "\n", inner, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).strip("\n")

def conv_table(inner):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", inner, re.S | re.I)
    out = []
    for i, r in enumerate(rows):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S | re.I)
        vals = []
        for c in cells:
            c = re.sub(r"<br\s*/?>", " ", c, flags=re.I)
            c = re.sub(r"<[^>]+>", "", c)
            c = html.unescape(c).replace("|", "\\|").strip()
            vals.append(c)
        if not vals:
            continue
        out.append("| " + " | ".join(vals) + " |")
        if i == 0:
            out.append("| " + " | ".join(["---"] * len(vals)) + " |")
    return "\n".join(out)

def html_to_md(s, imgdir, img_rel_prefix="images"):
    imgs = []
    pres = []
    tbls = []

    # 1) 抽出 pre
    def _pre(m):
        pres.append(conv_pre(m.group(1)))
        return "\n@@PRE%d@@\n" % (len(pres) - 1)
    s = re.sub(r"<pre[^>]*>(.*?)</pre>", _pre, s, flags=re.S | re.I)

    # 2) 抽出 table
    def _tbl(m):
        tbls.append(conv_table(m.group(1)))
        return "\n@@TBL%d@@\n" % (len(tbls) - 1)
    s = re.sub(r"<table[^>]*>(.*?)</table>", _tbl, s, flags=re.S | re.I)

    # 3) 抽出 img
    def _img(m):
        tag = m.group(0)
        mm = re.search(r'src="([^"]+)"', tag)
        if not mm:
            return ""
        url = mm.group(1)
        name = dl_image(url, imgdir)
        if name:
            imgs.append(name)
            return "\n@@IMG%d@@\n" % (len(imgs) - 1)
        return "\n<!-- 图片下载失败: %s -->\n" % url
    s = re.sub(r"<img[^>]*>", _img, s, flags=re.I)

    # 4) 链接
    s = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
               lambda m: "[%s](%s)" % (re.sub(r"<[^>]+>", "", m.group(2)).strip(), m.group(1)),
               s, flags=re.S | re.I)
    s = re.sub(r"<a[^>]*>(.*?)</a>", r"\1", s, flags=re.S | re.I)

    # 5) 标题
    for n in range(1, 7):
        s = re.sub(r"<h%d[^>]*>(.*?)</h%d>" % (n, n),
                   lambda m, n=n: "\n" + "#" * n + " " + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n",
                   s, flags=re.S | re.I)

    # 6) 结构标签
    s = re.sub(r"<hr\s*/?>", "\n---\n", s, flags=re.I)
    s = re.sub(r"<li[^>]*>", "\n- ", s, flags=re.I)
    s = re.sub(r"</li>", "", s, flags=re.I)
    s = re.sub(r"<blockquote[^>]*>", "\n> ", s, flags=re.I)
    s = re.sub(r"</blockquote>", "\n", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(div|p|tr|ul|ol|dl|dd|dt|h[1-6])>", "\n", s, flags=re.I)
    s = re.sub(r"<(div|p|tr|ul|ol|dl|dd|dt)[^>]*>", "\n", s, flags=re.I)

    # 7) 强调
    s = re.sub(r"</?(b|strong)[^>]*>", "**", s, flags=re.I)
    s = re.sub(r"</?(i|em)[^>]*>", "*", s, flags=re.I)
    s = re.sub(r"</?code[^>]*>", "`", s, flags=re.I)

    # 8) 去剩余标签
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)

    # 9) 回填占位符
    for i, p in enumerate(pres):
        s = s.replace("@@PRE%d@@" % i, "```\n" + p + "\n```")
    for i, t in enumerate(tbls):
        s = s.replace("@@TBL%d@@" % i, t)
    for i, n in enumerate(imgs):
        s = s.replace("@@IMG%d@@" % i, "![](%s/%s)" % (img_rel_prefix, n))

    # 10) 规整空白
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"\*\*\s*\*\*", "", s)
    return s.strip(), len(imgs)

def main():
    kw = None
    limit = None
    if "--dry" in sys.argv:
        kw = sys.argv[sys.argv.index("--dry") + 1]
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    targets = []
    for root, _, fs in os.walk(BASE):
        for fn in fs:
            if fn.endswith(".note"):
                p = os.path.join(root, fn)
                if kw and kw not in p:
                    continue
                targets.append(p)
    targets.sort()
    if limit:
        targets = targets[:limit]

    ok = bad = 0
    for p in targets:
        rel = os.path.relpath(p, BASE).replace("\\", "/")
        d = os.path.dirname(p)
        imgdir = os.path.join(d, "images")
        os.makedirs(imgdir, exist_ok=True)
        raw = io.open(p, encoding="utf-8", errors="replace").read().strip()
        # 某些 .note 外层包了一层 JSON/quoted，先尝试脱壳
        if raw.startswith('"') and raw.endswith('"'):
            try:
                raw = json.loads(raw)
            except Exception:
                pass
        try:
            md, nimg = html_to_md(raw, imgdir)
        except Exception as e:
            print("[ERR] %s -> %s" % (rel, e))
            bad += 1
            continue
        title = os.path.splitext(os.path.basename(p))[0]
        md = "# %s\n\n%s\n" % (title, md) if not md.startswith("# ") else md + "\n"
        outp = os.path.splitext(p)[0] + ".md"
        io.open(outp, "w", encoding="utf-8", newline="").write(md)
        print("[OK] %-70s %5d字 %3d图" % (rel[:70], len(md), nimg))
        ok += 1

    print("\n完成：成功 %d / 失败 %d / 共 %d" % (ok, bad, len(targets)))

if __name__ == "__main__":
    main()
