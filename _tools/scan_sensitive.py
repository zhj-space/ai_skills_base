# -*- coding: utf-8 -*-
"""推送前敏感扫描。给每周自动同步当安全闸用。

分两档：
  BLOCK  必须阻断——文件路径是凭据类，或正文出现明确的密码赋值
  WARN   只记进周报——出现邮箱、手机号、单独的敏感关键词（技术文档里很常见）

只看被 git 跟踪的文件。已被 .gitignore 排除的不算风险，因为推不上去。

退出码：有 BLOCK 返回 1，只有 WARN 返回 0。
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:/workspace/ai_kb_base")

# 路径命中即阻断：这类文件是原文凭据，不做脱敏。
# 只对 raw/ 生效——wiki/summaries 下的「（凭据已屏蔽）」页是脱敏副本，路径虽含
# "凭据/账号"字样但内容已抹除，不该误伤。
BLOCK_PATH = re.compile(r"(账号|密码|凭据|密钥|passwd|credential)", re.I)
BLOCK_PATH_SCOPE = "second-brain/raw/"

# 正文里的明确赋值式密码（不是"密码学""密码强度"这种讨论）
# 命中后还要看值的特征：占位符放行为 WARN，像真密码才 BLOCK。
#
# 2026-11-09 补漏：原来的规则只认 password/passwd + ASCII 冒号，
# 漏掉了 `pwd：<明文>` 这种「pwd 缩写 + 中文冒号」的写法，
# 导致一份含真实邮箱密码的原文被推到了 GitHub。教训：中文冒号必须显式覆盖。
#
# 2026-11-11 二次补漏：账号密码常写成 `账号/密码`（斜杠分隔），
# 或直接跟在「钱包：」后面，没有任何赋值符号。这类写法旧规则全抓不到。
# 另补 WIF 私钥（5H/5J/5K 开头、全 base58、48-62 字符）。
BLOCK_BODY = [
    re.compile(r"(?:密码|口令|密碼|密马)\s*[是为:：]\s*(\S{4,})"),
    re.compile(r"(?i)\b(?:password|passwd|pwd|pass)\s*[:：=]\s*(\S{4,})"),
    re.compile(r"(?i)\bapi[_-]?key\s*[:：=]\s*(\S{8,})"),
    re.compile(r"(?i)\bsecret\s*[:：=]\s*(\S{8,})"),
    re.compile(r"(?i)\btoken\s*[:：=]\s*(\S{12,})"),
    re.compile(r"(?i)\baccess[_-]?key\s*[:：=]\s*(\S{8,})"),
    re.compile(r"(?:账号|账户|帐号)\s*[是为:：]\s*(\S{4,}@\S+)"),
]

# 公认示例值：技术文档里遍地都是，泄露无实际危害
PLACEHOLDERS = {
    "123456", "12345678", "123456789", "1234567890", "password", "passwd",
    "root", "admin", "test", "000000", "111111", "abc123", "qwerty",
    "yourpassword", "your_password", "xxx", "x", "sa", "postgres",
    "mysql", "oracle", "hive", "sqoop", "test123", "admin123",
}

# 私钥整体出现，无论值多长都阻断
BLOCK_RAW = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    # v2ray / vmess 配置里的客户端 UUID，原文常注明「也是密码」。
    # 排除全 0 与全 1 这类明显示例值。
    re.compile(r'"id"\s*:\s*"(?!0{8}-|1{8}-)[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"'),
    # 区块链 WIF 私钥：5H/5J/5K 开头，全 base58，48-62 字符。
    # 长度放宽到 62 —— 早期只写 {48,50} 漏掉过一个 62 位的。
    re.compile(r"\b5[HJK][1-9A-HJ-NP-Za-km-z]{48,62}\b"),
    # 以太坊式 64 位 hex 私钥
    re.compile(r"\b0x[0-9a-fA-F]{64}\b"),
    # 注意：曾试过用「账号/密码」斜杠格式做规则，但正则分不清路径和凭据
    # （`second-brain/wiki/xxx` 会被误判），一次误报 607 处。
    # 结论：斜杠写法无法靠正则可靠识别，只能靠人工过一遍高风睑目录。
]

# 「钱包：」「私钥：」「助记词：」后面直接跟长串（没有赋值符号）
BLOCK_AFTER_LABEL = re.compile(
    r"(?:钱包|私钥|密钥|助记词|密语)\s*[:：]\s*\n*\s*([A-Za-z0-9+/=]{20,})"
)

WARN_BODY = [
    ("邮箱", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("手机号", re.compile(r"(?<![0-9])1[3-9][0-9]{9}(?![0-9])")),
    ("银行卡", re.compile(r"(?<![0-9])(?:62|4[0-9]|5[1-5])[0-9]{14,17}(?![0-9])")),
    ("身份证", re.compile(r"(?<![0-9])[1-9][0-9]{5}(?:19|20)[0-9]{2}(?:0[1-9]|1[0-2])[0-9]{2}[0-9]{3}[0-9Xx](?![0-9])")),
]


def tracked_files():
    """取被跟踪文件清单。

    必须用 -z（NUL 分隔）：默认模式下 git 会把中文路径转义成 \\346\\226\\207 这种
    八进制串，导致路径找不到文件、静默漏扫。这个坑一开始就踩了——
    第一次跑只扫到 120 个文件，实际有 1700+。
    """
    raw = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"])
    names = raw.decode("utf-8", "replace").split("\0")
    return [f for f in names if f and f.lower().endswith((".md", ".txt", ".json", ".yml", ".yaml"))]


def main() -> int:
    blocks, warns = [], []
    for rel in tracked_files():
        p = ROOT / rel
        if not p.is_file():
            continue
        if rel.startswith(BLOCK_PATH_SCOPE) and BLOCK_PATH.search(Path(rel).name):
            blocks.append((rel, "路径是凭据类原文", 0))
            continue
        try:
            text = p.read_bytes().decode("utf-8", "replace")
        except OSError:
            continue
        for pat in BLOCK_RAW:
            if pat.search(text):
                blocks.append((rel, "含私钥块", 1))
                break
        else:
            m_lbl = BLOCK_AFTER_LABEL.search(text)
            if m_lbl:
                blocks.append((rel, "「钱包/私钥」标签后跟长串", 1))
                for name, pat in WARN_BODY:
                    if pat.search(text):
                        warns.append((rel, name, 1))
                continue
            hit = None
            for pat in BLOCK_BODY:
                for m in pat.finditer(text):
                    val = m.group(1).strip("'\"`()[]{}<>,;")
                    if not val:
                        continue
                    if val.lower() in PLACEHOLDERS or len(val) <= 3:
                        hit = ("warn", val)
                    else:
                        hit = ("block", val)
                        break
                if hit and hit[0] == "block":
                    break
            if hit and hit[0] == "block":
                blocks.append((rel, f"密码/密钥赋值，值长 {len(hit[1])}", 1))
            elif hit:
                warns.append((rel, "密码赋值（占位符）", 1))
        for name, pat in WARN_BODY:
            n = len(pat.findall(text))
            if n:
                warns.append((rel, name, n))

    print(f"扫描范围：{len(tracked_files())} 个被跟踪文件\n")

    if blocks:
        print(f"[BLOCK] {len(blocks)} 处，必须处理后再推送")
        for rel, why, n in blocks[:20]:
            print(f"   {rel}　←　{why}")
        if len(blocks) > 20:
            print(f"   …… 另有 {len(blocks)-20} 处")
    else:
        print("[BLOCK] 无")

    print()
    if warns:
        agg = {}
        for rel, name, n in warns:
            agg[name] = agg.get(name, 0) + 1
        print(f"[WARN] {len(warns)} 处，记进周报即可")
        for name, c in sorted(agg.items(), key=lambda x: -x[1]):
            print(f"   {name}：{c} 个文件")
        print("   明细：")
        for rel, name, n in warns[:12]:
            print(f"     {name}×{n}  {rel}")
        if len(warns) > 12:
            print(f"     …… 另有 {len(warns)-12} 处")
    else:
        print("[WARN] 无")

    print()
    if blocks:
        print("结论：不允许推送。先处理 BLOCK 项。")
        return 1
    print("结论：可以推送。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
