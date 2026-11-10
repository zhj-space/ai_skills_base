"""验证 recompile.py 能检出 raw 改动。改一个字→检测→还原。"""
import io
import os
import shutil
import subprocess
import sys

RAW = r"D:/workspace/ai_kb_base/second-brain/raw/docs/personal-assets/python/getting-started/Python IO.md"
TOOLS = r"D:/workspace/ai_kb_base/_tools"
BAK = RAW + ".bak_rc"

OLD = "最简单的输出方法是用print语句"
NEW = "最简单的输出手段是用print语句"

shutil.copy2(RAW, BAK)
try:
    s = io.open(RAW, encoding="utf-8").read()
    assert OLD in s, "目标句未找到"

    print("① 改动前")
    subprocess.run([sys.executable, "recompile.py"], cwd=TOOLS)

    io.open(RAW, "w", encoding="utf-8", newline="").write(s.replace(OLD, NEW, 1))
    print("\n② 改动一个字后")
    subprocess.run([sys.executable, "recompile.py"], cwd=TOOLS)
finally:
    shutil.copy2(BAK, RAW)
    os.remove(BAK)
    print("\n③ 已还原")
    subprocess.run([sys.executable, "recompile.py"], cwd=TOOLS)
