# -*- coding: utf-8 -*-
"""
gen_ingest_log.py — 每次入库后生成处理日志。

用法：
    python gen_ingest_log.py --title "同济版高数知识点梳理" ^
        --src "raw/docs/personal-assets/数学/同济版高数知识点梳理.md" ^
        --docs "2026-11-06-同济版高数知识点梳理.md" ^
        --new-concepts "极限,连续与间断,导数与微分" ^
        --append-concepts "实数完备性" ^
        --digests ""

日志写到 <工作区>/logs/YYYY-MM-DD-<标题>.md，内容含：
原始是什么、生成了哪些文档页/概念页/沉淀页、校验结果。
"""
import io, os, re, sys, json, argparse, datetime, subprocess

WS = r"D:/workspace/ai_kb_base"
KB = os.path.join(WS, "second-brain")
TOOLS = os.path.join(WS, "_tools")
LOGS = os.path.join(WS, "logs")


def read(p):
    return io.open(p, encoding="utf-8").read()


def count_claims(path):
    s = read(path)
    return len(re.findall(r"^\- .*\`(high|medium|low)\`\s*$", s, re.M))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--src", required=True, help="原文相对 second-brain 的路径")
    ap.add_argument("--docs", default="", help="文档页文件名，逗号分隔")
    ap.add_argument("--new-concepts", default="", help="新建概念页名，逗号分隔")
    ap.add_argument("--append-concepts", default="", help="追加的概念页名，逗号分隔")
    ap.add_argument("--digests", default="", help="沉淀页文件名，逗号分隔")
    ap.add_argument("--form", default="", help="原文形态：有章节 / 无章节")
    ap.add_argument("--note", default="", help="补充说明")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    args = ap.parse_args()

    src_abs = os.path.join(KB, args.src)
    src_txt = read(src_abs) if os.path.exists(src_abs) else ""
    wc = re.search(r"^word_count:\s*(\d+)", src_txt, re.M)
    word_count = wc.group(1) if wc else "?"
    lines = src_txt.count("\n") + 1

    docs = [x for x in args.docs.split(",") if x.strip()]
    new_c = [x for x in args.new_concepts.split(",") if x.strip()]
    app_c = [x for x in args.append_concepts.split(",") if x.strip()]
    digs = [x for x in args.digests.split(",") if x.strip()]

    # 校验：全库断言 + 保留率
    claims_out = subprocess.run([sys.executable, os.path.join(TOOLS, "check_claims.py"), "--all"],
                                capture_output=True, text=True).stdout
    m = re.search(r"逐字通过 (\d+) 条 / 不匹配 (\d+) 条", claims_out)
    claims_txt = "%s 条逐字通过，%s 条不匹配" % (m.group(1), m.group(2)) if m else "未取到"

    pages = [os.path.join(KB, "wiki", "summaries", d) for d in docs] \
            + [os.path.join(KB, "wiki", "concepts", c + ".md") for c in new_c + app_c]
    cov_txt = "未计算"
    if pages:
        cov = subprocess.run([sys.executable, os.path.join(TOOLS, "check_coverage.py"), src_abs] + pages,
                             capture_output=True, text=True).stdout
        m2 = re.search(r"实质内容保留率：([\d.]+)%", cov)
        if m2:
            cov_txt = m2.group(1) + "%"

    L = []
    A = L.append
    A("# 处理日志 · %s · %s" % (args.date, args.title))
    A("")
    A("## 一、原始是什么")
    A("")
    A("| 项 | 内容 |")
    A("|---|---|")
    A("| 原文 | `%s` |" % args.src)
    A("| 规模 | %s 字 / %d 行 |" % (word_count, lines))
    if args.form:
        A("| 形态 | %s |" % args.form)
    # 同目录原件
    src_dir = os.path.dirname(src_abs)
    if os.path.isdir(src_dir):
        base = os.path.splitext(os.path.basename(src_abs))[0]
        for ext in (".html", ".pdf", ".docx"):
            orig = os.path.join(src_dir, base + ext)
            if os.path.exists(orig):
                A("| 原件 | 同目录 `%s`（%.1f KB） |" % (base + ext, os.path.getsize(orig)/1024))
    A("")
    if args.note:
        A(args.note)
        A("")

    A("## 二、生成了什么")
    A("")
    A("### 文档页（%d 个）" % len(docs))
    A("")
    if docs:
        for d in docs:
            p = os.path.join(KB, "wiki", "summaries", d)
            if os.path.exists(p):
                s = read(p)
                A("- `%s` —— %d 行 / %.1f KB / %d 条断言" % (
                    d, s.count("\n")+1, len(s.encode("utf-8"))/1024, count_claims(p)))
            else:
                A("- `%s`（未找到文件）" % d)
    else:
        A("- 无")
    A("")

    A("### 概念页（新建 %d 个，追加 %d 个）" % (len(new_c), len(app_c)))
    A("")
    if new_c:
        A("**新建**：")
        A("")
        for c in new_c:
            p = os.path.join(KB, "wiki", "concepts", c + ".md")
            if os.path.exists(p):
                s = read(p)
                A("- [[%s]] —— %d 行 / %.1f KB" % (c, s.count("\n")+1, len(s.encode("utf-8"))/1024))
            else:
                A("- [[%s]]（未找到文件）" % c)
        A("")
    if app_c:
        A("**追加**：")
        A("")
        for c in app_c:
            A("- [[%s]]" % c)
        A("")
    if not new_c and not app_c:
        A("- 无")
        A("")

    A("### 沉淀页（%d 个）" % len(digs))
    A("")
    if digs:
        for d in digs:
            A("- [[%s]]" % d)
    else:
        A("- 无（本篇为资料编译，未产生问答沉淀）")
    A("")

    A("## 三、索引与主题地图")
    A("")
    A("- `index.md` 已重建（含文档页、概念页、沉淀页清单）")
    A("- `wiki/topic-map.md` 已更新相关分组")
    A("")

    A("## 四、校验结果")
    A("")
    A("| 项 | 结果 |")
    A("|---|---|")
    A("| 断言逐字校验 | %s |" % claims_txt)
    A("| 实质保留率 | %s |" % cov_txt)
    A("")

    os.makedirs(LOGS, exist_ok=True)
    out = os.path.join(LOGS, "%s-%s.md" % (args.date, args.title))
    io.open(out, "w", encoding="utf-8", newline="").write("\n".join(L))
    print("已写入：%s" % out)
    print("文档页 %d · 新建概念 %d · 追加概念 %d · 沉淀 %d" % (len(docs), len(new_c), len(app_c), len(digs)))
    print("断言：%s；保留率：%s" % (claims_txt, cov_txt))


if __name__ == "__main__":
    main()
