# -*- coding: utf-8 -*-
"""规范稽查：字段完整性、段骨架、文件名一致性、编号格式。

与另外两个校验脚本的分工：
  check_claims.py   —— 断言有没有抄对原文（内容真实性）
  check_ontology.py —— 类型与关系合不合法（结构合法性）
  check_spec.py     —— 格式与骨架符不符合规范（书写规范）  ← 本脚本

判定分两级：
  error  必须修，否则页面不符合 agent.md 的约定
  warn   建议修，多数是历史遗留

退出码：有 error 返回 1，否则 0。
"""
import re
import sys
from pathlib import Path

KB = Path(r"D:/workspace/ai_kb_base/second-brain/wiki")

# ── 各类型页面的必填 frontmatter 字段 ──────────────────────────────
REQUIRED = {
    "concept": ["type", "name", "aliases", "updated"],
    "entity": ["type", "name", "aliases", "entity_type", "updated"],
    "method": ["type", "name", "aliases", "updated"],
    "metric": ["type", "name", "aliases", "updated"],
    "doc": ["type", "title", "source_path", "raw_hash"],
    "analysis": ["type", "title"],
}

# doc_id 是后来才加的约定，早期 304 篇文档页没有，属历史遗留，只报 warn
SOFT_FIELDS = {"doc": ["doc_id"]}

# 目录 → 允许的 type（一个目录可能有多种合法类型）
DIR_TYPE = {
    "concepts": ["concept"],
    "entities": ["entity"],
    "methods": ["method"],
    "metrics": ["metric"],
    "summaries": ["doc"],
    # analysis 目录里除了沉淀页，还有 digest 索引页与 digest-index.md
    "analysis": ["analysis", "digest", "index"],
}
CONCEPT_SECTIONS = [
    "是什么",
    "怎样理解 · 为什么",
    "有什么性质",
    "怎么用",
    "关系",
    "常见误区",
    "出处",
]

# ── 文档页必需段（原文全文为可选段）──────────────────────────────
DOC_SECTIONS = ["摘要", "关键断言", "涉及概念", "原文位置"]

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# 知识点编号：2.1-D / 3.2-P5 / 4-U3
KP_NO = re.compile(r"\b\d+(?:\.\d+)?-[DPU]\d+\b")

errors, warns = [], []


def parse_fm(text):
    m = FM.match(text)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def sections(text):
    """取二级标题名，按出现顺序。"""
    body = FM.sub("", text, count=1)
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", body, re.M)]


def main() -> int:
    checked = 0
    for sub, expect_types in DIR_TYPE.items():
        d = KB / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.startswith("_"):
                continue
            rel = f"{sub}/{p.name}"
            raw_bytes = p.read_bytes()
            # 换行检查：本库约定 LF。CRLF 会让正则和逐字比对全部失效，
            # 而且 .gitattributes 设了 * -text，混进来就再也自动修不回去。
            if b"\r\n" in raw_bytes:
                errors.append((rel, "换行符是 CRLF，本库约定 LF"))
            # 解析前统一成 LF，避免 CRLF 文件被误判为「缺少 frontmatter」
            text = raw_bytes.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")
            fm = parse_fm(text)
            checked += 1

            # 1 frontmatter 存在且 type 在允许集合内
            if fm is None:
                errors.append((rel, "缺少 frontmatter"))
                continue
            got_type = fm.get("type", "")
            if got_type not in expect_types:
                errors.append((rel, f"type 应为 {'/'.join(expect_types)}，实际 {got_type or '空'}"))

            # 2 必填字段（硬）
            for k in REQUIRED.get(got_type, []):
                if not fm.get(k):
                    errors.append((rel, f"缺必填字段 {k}"))
            # 2b 建议字段（历史遗留，只警告不阻断）
            for k in SOFT_FIELDS.get(got_type, []):
                if not fm.get(k):
                    warns.append((rel, f"缺建议字段 {k}（历史遗留，可不补）"))

            # 3 文件名 = name（四类知识节点的约定）
            name = fm.get("name", "")
            stem = p.stem
            if got_type in ("concept", "entity", "method", "metric") and name and name != stem:
                errors.append((rel, f"文件名与 name 不一致：文件 {stem} / name {name}"))

            # 4 updated 格式
            upd = fm.get("updated", "")
            if upd and not DATE.match(upd):
                warns.append((rel, f"updated 格式应为 YYYY-MM-DD，实际 {upd}"))

            # 5 aliases 非空
            aliases = fm.get("aliases", "")
            if got_type in ("concept", "entity", "method", "metric") and aliases in ("", "[]"):
                warns.append((rel, "aliases 为空"))

            # 6 段骨架
            # 「知识点总索引」由 build_kp_index.py 按章罗列生成，结构本就是清单，
            # 不是普通文档页的五段式，因此豁免骨架检查。
            secs = sections(text)
            if "知识点总索引" in p.name:
                pass
            elif got_type == "concept":
                missing = [s for s in CONCEPT_SECTIONS if s not in secs]
                if missing:
                    errors.append((rel, "缺段：" + "、".join(missing)))
                else:
                    order = [secs.index(s) for s in CONCEPT_SECTIONS]
                    if order != sorted(order):
                        errors.append((rel, "七段顺序错乱"))
            elif got_type == "doc":
                missing = [s for s in DOC_SECTIONS if s not in secs]
                if missing:
                    errors.append((rel, "缺段：" + "、".join(missing)))

            # 7 编号格式（仅在出现编号时检查，不强求每个页面都有）
            body = FM.sub("", text, count=1)
            for m in re.finditer(r"`?(\d+\.\d+-[A-Za-z]+\d+)`?", body):
                if not KP_NO.fullmatch(m.group(1)):
                    warns.append((rel, f"编号格式可疑：{m.group(1)}"))

    print(f"稽查范围：{checked} 个页面\n")

    if errors:
        from collections import Counter
        print(f"[ERROR] {len(errors)} 处")
        for msg, n in Counter(m for _, m in errors).most_common(10):
            print(f"   {msg} × {n}")
        print("\n   明细（前 20 条）：")
        for rel, msg in errors[:20]:
            print(f"     {rel}　←　{msg}")
        if len(errors) > 20:
            print(f"     …… 另有 {len(errors)-20} 条")
    else:
        print("[ERROR] 无")

    print()
    if warns:
        print(f"[WARN] {len(warns)} 处")
        for rel, msg in warns[:12]:
            print(f"   {rel}　←　{msg}")
        if len(warns) > 12:
            print(f"   …… 另有 {len(warns)-12} 条")
    else:
        print("[WARN] 无")

    print()
    if errors:
        print("结论：有 error，需修正。")
        return 1
    print("结论：规范检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
