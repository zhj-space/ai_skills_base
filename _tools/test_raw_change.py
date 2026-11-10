"""实测：raw 改三个字后，文档页断言会不会失效。改完立即还原。"""
import io
import shutil
import subprocess
import sys
import os

KB = r"D:/workspace/ai_kb_base/second-brain"
RAW = os.path.join(KB, "raw/docs/personal-assets/python/getting-started/Python IO.md")
DOC = os.path.join(KB, "wiki/summaries/2026-11-06-Python标准IO.md")
TOOLS = r"D:/workspace/ai_kb_base/_tools"
BAK = RAW + ".bak_test"

OLD = "你可以给它传递零个或多个用逗号隔开的表达式"
NEW = "你可以给它传递多个用逗号隔开的表达式"


def run_check():
    r = subprocess.run([sys.executable, "check_claims.py", DOC],
                       cwd=TOOLS, capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "") + (r.stderr or "")
    for ln in out.strip().split("\n")[-3:]:
        if ln.strip():
            print("    " + ln.strip())
    return out


shutil.copy2(RAW, BAK)
try:
    s = io.open(RAW, encoding="utf-8").read()
    if OLD not in s:
        print("!! 原文未找到目标句，测试中止")
        sys.exit(1)

    print("① 改动前")
    run_check()

    print("\n② 把原文「零个或多个」改成「多个」")
    io.open(RAW, "w", encoding="utf-8", newline="").write(s.replace(OLD, NEW, 1))
    run_check()

    print("\n③ 还原原文")
    shutil.copy2(BAK, RAW)
    run_check()
finally:
    if os.path.exists(BAK):
        shutil.copy2(BAK, RAW)
        os.remove(BAK)
    print("\n已确认原文与备份均已还原")
