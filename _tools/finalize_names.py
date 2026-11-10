# -*- coding: utf-8 -*-
"""收尾：文件名对齐 + 图片型笔记生成 md"""
import os, io, shutil, re

BASE = r"D:/workspace/ai_kb_base/_ynote_export"
P = "个人资产体系"

# 1) 文件名被 HTML 污染 / 被转义的，改回正常名
renames = [
    (P + "/android/Ibm Worklight/方法/_a  href=tel15915749720xxx_a的作用.md",
     P + "/android/Ibm Worklight/方法/a的作用.md", "a的作用"),
    (P + "/android/Ibm Worklight/adapter/关于传递参数有_(不等于)时出现的问题。(1).md",
     P + "/android/Ibm Worklight/adapter/关于传递参数有(不等于)时出现的问题。(1).md", None),
]
for src, dst, fix_h1 in renames:
    sp, dp = os.path.join(BASE, src), os.path.join(BASE, dst)
    if not os.path.exists(sp):
        print("[SKIP] 源不存在 %s" % src)
        continue
    if fix_h1:
        s = io.open(sp, encoding="utf-8").read()
        s = re.sub(r"^# .*$", "# " + fix_h1, s, count=1, flags=re.M)
        io.open(sp, "w", encoding="utf-8", newline="").write(s)
    if os.path.exists(dp):
        os.remove(dp)
    os.rename(sp, dp)
    print("[RENAME] %s -> %s" % (os.path.basename(src), os.path.basename(dst)))

# 2) 纯图片笔记：人工智能学习图谱.png -> md
png = os.path.join(BASE, P, "机器学习/人工智能学习图谱.png")
if os.path.exists(png):
    imgdir = os.path.join(BASE, P, "机器学习/images")
    os.makedirs(imgdir, exist_ok=True)
    dstpng = os.path.join(imgdir, "人工智能学习图谱.png")
    shutil.copy2(png, dstpng)
    md = "# 人工智能学习图谱\n\n> 该笔记正文为一张脑图图片（导出自有道云原图）。\n\n![](images/人工智能学习图谱.png)\n"
    io.open(os.path.join(BASE, P, "机器学习/人工智能学习图谱.md"), "w", encoding="utf-8", newline="").write(md)
    print("[IMG-NOTE] 人工智能学习图谱.md 已生成（图片 %.0f KB）" % (os.path.getsize(dstpng) / 1024))

# 3) 清理中间件（.note / .mindmap 留在导出区，不删，后面统一归档）
print("\n收尾完成")
