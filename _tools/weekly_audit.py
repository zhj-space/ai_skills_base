#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""weekly_audit.py — 知识库周检：七项体检 + 上周对比 + 周报落盘

用法
    python _tools/weekly_audit.py            跑完写 logs/weekly/<今天>.md 和 .json
    python _tools/weekly_audit.py --dry      只打印，不写盘
    python _tools/weekly_audit.py --json     只输出 JSON（给程序用）

退出码
    0  全绿，或只有黄项（观察即可）
    1  有红项（需要人处理）

设计原则
    脚本只做「采集 + 判定 + 出骨架」，不做任何修改。
    解读、建议、决策项由执行它的 agent 补到周报里。
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "second-brain"
TOOLS = ROOT / "_tools"
OUT = ROOT / "logs" / "weekly"

# 白名单已废弃：verify_kb.py 现在会跳过代码块与反引号内的示例，
# 剩下的断链都是真的。保留空集只是为了让下面的判断逻辑不用改。
LINK_WHITELIST = set()


def run(args, timeout=300):
    """跑一个检查脚本，返回 (退出码, 输出文本)"""
    try:
        p = subprocess.run(
            [sys.executable, str(args[0])] + [str(a) for a in args[1:]],
            capture_output=True, timeout=timeout,
        )
        out = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
        return p.returncode, out
    except subprocess.TimeoutExpired:
        return 124, f"[超时] 超过 {timeout} 秒"
    except Exception as e:  # noqa: BLE001
        return 125, f"[调用失败] {e}"


def grab(pattern, text, cast=int):
    m = re.search(pattern, text)
    if not m:
        return None
    try:
        return cast(m.group(1))
    except (ValueError, IndexError):
        return None


def count_md(base: Path):
    return len(list(base.glob("*.md"))) if base.is_dir() else 0


def raw_files():
    base = KB / "raw"
    if not base.is_dir():
        return set()
    return {p.relative_to(KB).as_posix() for p in base.rglob("*.md")}


def summary_sources():
    """从 summaries 页 frontmatter 里抽出 source_path"""
    base = KB / "wiki" / "summaries"
    found = set()
    if not base.is_dir():
        return found
    for p in base.glob("*.md"):
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:800]
        except OSError:
            continue
        m = re.search(r"^source_path:\s*[\"']?([^\"'\n]+)", head, re.M)
        if m:
            found.add(m.group(1).strip().replace("\\", "/"))
    return found


def collect():
    r = {"date": date.today().isoformat(), "metrics": {}, "checks": {}, "todos": []}
    m = r["metrics"]

    # 1 链接
    rc, out = run([TOOLS / "sync_skills.py", "--check"])
    r["checks"]["link"] = {"rc": rc, "detail": out.strip().splitlines()[-1] if out.strip() else ""}

    # 2 本体约束
    rc, out = run([TOOLS / "check_ontology.py"])
    m["ontology_error"] = grab(r"合计：error (\d+) 处", out)
    m["ontology_warn"] = grab(r"合计：error \d+ 处 · warn (\d+) 处", out)
    m["nodes"] = grab(r"知识节点 (\d+)", out)
    m["relations"] = grab(r"关系条目 (\d+)", out)
    r["checks"]["ontology"] = {"rc": rc}

    # 3 断言逐字
    rc, out = run([TOOLS / "check_claims.py", "--all"])
    m["claims_pass"] = grab(r"逐字通过 (\d+) 条", out)
    m["claims_fail"] = grab(r"不匹配 (\d+) 条", out)
    r["checks"]["claims"] = {"rc": rc}

    # 4 结构
    rc, out = run([TOOLS / "verify_kb.py"])
    m["total_md"] = grab(r"全库 md：(\d+) 篇", out)
    m["broken_links"] = grab(r"断链：(\d+) 个目标", out)
    m["islands"] = grab(r"孤岛页（无入链）：(\d+)", out)
    m["islands_sensitive"] = grab(r"其中敏感隔离页（凭据类）：(\d+)", out)
    m["img_missing"] = grab(r"图片引用缺失：(\d+) 处", out)
    m["img_total"] = grab(r"图片引用总数：(\d+)", out)
    m["src_ok"] = grab(r"sources 内容状态：ok (\d+)", out)
    m["src_bad"] = grab(r"ok \d+ / 非 ok (\d+)", out)
    real = []
    for line in out.splitlines():
        mm = re.match(r"\s+\[\[(.+?)\]\]\s+被引用", line)
        if mm and mm.group(1) not in LINK_WHITELIST:
            real.append(mm.group(1))
    m["broken_real"] = len(real)
    m["broken_names"] = real
    r["checks"]["structure"] = {"rc": rc}

    # 5 raw 变更
    rc, out = run([TOOLS / "recompile.py"])
    m["raw_changed"] = grab(r"已变 (\d+)", out)
    m["raw_lost"] = grab(r"原文丢失 (\d+)", out)
    m["raw_nohash"] = grab(r"无指纹 (\d+)", out)
    m["raw_nosrc"] = grab(r"无 source_path (\d+)", out)
    m["raw_total"] = grab(r"文档页 (\d+) 篇", out)
    r["checks"]["raw"] = {"rc": rc}

    # 6 覆盖
    raws = raw_files()
    covered = summary_sources()
    missing = sorted(raws - covered)
    m["raw_count"] = len(raws)
    m["summaries"] = count_md(KB / "wiki" / "summaries")
    m["coverage_pct"] = round(len(covered & raws) / len(raws) * 100, 1) if raws else 0.0
    m["missing_pages"] = missing
    r["checks"]["coverage"] = {"rc": 0}

    # 7 沉淀库
    ana = [p for p in (KB / "wiki" / "analysis").glob("*.md") if p.name != "digest-index.md"]
    m["analysis"] = len(ana)
    idx = KB / "wiki" / "analysis" / "digest-index.md"
    m["digest_entries"] = 0
    if idx.is_file():
        m["digest_entries"] = len(re.findall(r"^\s*[-*]\s*\[\[", idx.read_text(encoding="utf-8", errors="replace"), re.M))
    m["concepts"] = count_md(KB / "wiki" / "concepts")
    m["entities"] = count_md(KB / "wiki" / "entities")
    m["methods"] = count_md(KB / "wiki" / "methods")
    m["metrics_pages"] = count_md(KB / "wiki" / "metrics")
    r["checks"]["digest"] = {"rc": 0}

    # 判定
    red, yellow = [], []
    if r["checks"]["link"]["rc"] != 0:
        red.append("skill 链接已断，两个路径变成两份独立文件")
    if m["ontology_error"]:
        red.append(f"本体约束 error {m['ontology_error']} 处")
    if m["claims_fail"]:
        red.append(f"断言逐字不匹配 {m['claims_fail']} 条")
    if m["broken_real"]:
        red.append(f"真实断链 {m['broken_real']} 处：{', '.join(m['broken_names'][:5])}")
    if m["img_missing"]:
        red.append(f"图片引用缺失 {m['img_missing']} 处")
    if m["raw_lost"]:
        red.append(f"原文丢失 {m['raw_lost']} 篇（文档页指着的被删了）")

    if m["raw_changed"]:
        yellow.append(f"原文变更 {m['raw_changed']} 篇，需要重编译受影响页面")
    if m["raw_nohash"]:
        yellow.append(f"{m['raw_nohash']} 篇原文没有指纹，变更感知失效")
    if m["missing_pages"]:
        yellow.append(f"{len(m['missing_pages'])} 篇原文没有文档页（覆盖率 {m['coverage_pct']}%）")
    if m["analysis"] > m["digest_entries"]:
        yellow.append(f"沉淀库 {m['analysis']} 篇，digest-index 只登记 {m['digest_entries']} 条")

    for t in red:
        r["todos"].append({"level": "红", "text": t})
    for t in yellow:
        r["todos"].append({"level": "黄", "text": t})
    r["level"] = "red" if red else ("yellow" if yellow else "green")
    return r


def prev_report(today: str):
    if not OUT.is_dir():
        return None
    files = sorted(p for p in OUT.glob("*.json") if p.stem < today)
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def trend(cur, old):
    if old is None or cur is None:
        return "—"
    if cur == old:
        return "持平"
    d = abs(cur - old)
    if isinstance(d, float):
        d = round(d, 1)
    return ("↑" if cur > old else "↓") + f" {d}"


def render(r, prev):
    m, pm = r["metrics"], (prev or {}).get("metrics", {})
    icon = {"green": "🟢 全绿", "yellow": "🟡 有观察项", "red": "🔴 有异常"}[r["level"]]
    L = [f"# 知识库周检 · {r['date']}", "", f"**状态：{icon}**", ""]

    L += ["## 一、硬指标", "", "| 指标 | 本周 | 上周 | 变化 |", "|---|---|---|---|"]
    rows = [
        ("本体约束 error", "ontology_error"), ("本体约束 warn", "ontology_warn"),
        ("断言逐字通过", "claims_pass"), ("断言不匹配", "claims_fail"),
        ("真实断链", "broken_real"), ("孤岛页", "islands"),
        ("其中敏感隔离页", "islands_sensitive"),
        ("图片缺失", "img_missing"), ("原文变更", "raw_changed"),
        ("原文丢失", "raw_lost"), ("无指纹原文", "raw_nohash"),
        ("覆盖率 %", "coverage_pct"), ("概念页", "concepts"),
    ]
    for label, key in rows:
        L.append(f"| {label} | {m.get(key)} | {pm.get(key, '—')} | {trend(m.get(key), pm.get(key))} |")

    L += ["", "## 二、库体量", "", "| 项 | 数量 |", "|---|---|"]
    for label, key in [("全库 md", "total_md"), ("原文 raw", "raw_count"),
                       ("文档页 summaries", "summaries"), ("概念页", "concepts"),
                       ("实体页", "entities"), ("方法页", "methods"), ("指标页", "metrics_pages"),
                       ("知识节点", "nodes"), ("关系条目", "relations"),
                       ("沉淀 analysis", "analysis"), ("digest 索引条目", "digest_entries"),
                       ("图片引用", "img_total")]:
        L.append(f"| {label} | {m.get(key)} |")

    L += ["", "## 三、raw 变更追踪", ""]
    if m.get("raw_changed"):
        L.append(f"- 已变 **{m['raw_changed']}** 篇，需重编译受影响页面")
        L.append(f"- 原文丢失 {m.get('raw_lost')} 篇 · 无指纹 {m.get('raw_nohash')} 篇")
        L.append("")
        L.append("> 明细跑 `python _tools/recompile.py` 看清单")
    else:
        L.append("本轮没有检测到原文变更。")

    L += ["", "## 四、覆盖缺口", ""]
    miss = m.get("missing_pages") or []
    if miss:
        L.append(f"共 {len(miss)} 篇原文没有对应文档页（覆盖率 {m.get('coverage_pct')}%）：")
        L.append("")
        for p in miss[:20]:
            L.append(f"- `{p}`")
        if len(miss) > 20:
            L.append(f"- …… 另有 {len(miss) - 20} 篇")
    else:
        L.append("全部原文都有对应文档页。")

    L += ["", "## 五、等你决策", ""]
    if r["todos"]:
        for t in r["todos"]:
            L.append(f"- **[{t['level']}]** {t['text']}")
    else:
        L.append("本周没有需要决策的事项。")

    L += ["", "## 六、建议动作", "", "> 由执行本次周检的 agent 补充", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="知识库周检")
    ap.add_argument("--dry", action="store_true", help="只打印不写盘")
    ap.add_argument("--json", action="store_true", help="只输出 JSON")
    args = ap.parse_args()

    r = collect()
    prev = prev_report(r["date"])

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 1 if r["level"] == "red" else 0

    md = render(r, prev)
    if args.dry:
        print(md)
        return 1 if r["level"] == "red" else 0

    OUT.mkdir(parents=True, exist_ok=True)
    mp = OUT / f"{r['date']}.md"
    jp = OUT / f"{r['date']}.json"
    mp.write_text(md, encoding="utf-8", newline="\n")
    jp.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    m = r["metrics"]
    print(f"[{'红' if r['level'] == 'red' else '黄' if r['level'] == 'yellow' else '绿'}] 周检完成 {r['date']}")
    print(f"  本体 error {m['ontology_error']} / warn {m['ontology_warn']}"
          f" · 断言 {m['claims_pass']} 通过 {m['claims_fail']} 不匹配"
          f" · 断链 {m['broken_real']} 真实 / {m['broken_links']} 目标"
          f" · 图片缺失 {m['img_missing']}")
    print(f"  覆盖 {m['coverage_pct']}%（{m['summaries']}/{m['raw_count']}）"
          f" · 原文变更 {m['raw_changed']} · 沉淀 {m['analysis']} 篇")
    print(f"  周报 {mp}")
    print(f"  数据 {jp}")
    if r["todos"]:
        print("  待办：")
        for t in r["todos"]:
            print(f"    [{t['level']}] {t['text']}")
    return 1 if r["level"] == "red" else 0


if __name__ == "__main__":
    sys.exit(main())
