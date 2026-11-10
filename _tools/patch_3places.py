# -*- coding: utf-8 -*-
"""补回 3 处新版导出缺失的文字（依据旧版 sources 的有道 API 原文）"""
import sys, io, os

EXPORT = r"D:/workspace/ai_kb_base/_ynote_export"

patches = [
    # (相对路径, 旧片段, 新片段, 说明)
    (
        "个人资产体系/数据库/pgsql/常用的sql.md",
        "| chown -R  postgres:postgres | ",
        "| chown -R  postgres:postgres/mnt/sdc/pg_data/tbs_duzk 把文件夹所有者更改为postgres组postgres用户 | ",
        "pgsql chown 单元格截断",
    ),
    (
        "个人资产体系/数据库/pgsql/常用的sql.md",
        "| GRANT USAGE ON SCHEMA yanghui TO | ",
        "| GRANT USAGE ON SCHEMA yanghui TOliuhaiying; | ",
        "pgsql GRANT USAGE 截断",
    ),
    (
        "个人资产体系/数据库/pgsql/常用的sql.md",
        "| grant select | ",
        "| grant selectON ALL TABLES IN SCHEMA yanghuito liuhaiying; | ",
        "pgsql grant select 截断",
    ),
    (
        "个人资产体系/数据库/pgsql/常用的sql.md",
        "| alter default privileges for user yanghui in  schema yanghui | ",
        "| alter default privileges for user yanghui in  schema yanghuigrant select ontables to liuhaiying; | ",
        "pgsql alter default privileges 截断",
    ),
    (
        "个人资产体系/大数据/Spark/大数据调优-spark调优.md",
        "[https://www.jianshu.com/p/b8841a8925fb](https://www.jianshu.com/p/b8841a8925fb)\n",
        "spark性能优化（包括优化原理及基本方法）\n\n[https://www.jianshu.com/p/b8841a8925fb](https://www.jianshu.com/p/b8841a8925fb)\n",
        "spark调优 缺链接锚文本",
    ),
    (
        "个人资产体系/大数据/Spark/spark计算模型-深入理解spark架构和原理.md",
        "![](images/WEBRESOURCEf993f9340fb8f6e714b63369421b504dstickPicture.png)\n\n数据写入的简要流程：",
        "![](images/WEBRESOURCEf993f9340fb8f6e714b63369421b504dstickPicture.png)\n\n### **1.8.2数据写入过程分析**\n\n数据写入的简要流程：",
        "spark计算模型 缺 1.8.2 小标题",
    ),
]

ok = 0
fail = []
for rel, old, new, desc in patches:
    p = os.path.join(EXPORT, rel)
    if not os.path.exists(p):
        fail.append((desc, "文件不存在"))
        continue
    s = io.open(p, encoding="utf-8").read()
    cnt = s.count(old)
    if cnt == 0:
        fail.append((desc, "未找到匹配片段"))
        continue
    if cnt > 1:
        fail.append((desc, "匹配到 %d 处，需人工确认" % cnt))
        continue
    s = s.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    ok += 1
    print("[OK] %s" % desc)

print("\n成功 %d / %d" % (ok, len(patches)))
for d, r in fail:
    print("[FAIL] %s -> %s" % (d, r))
