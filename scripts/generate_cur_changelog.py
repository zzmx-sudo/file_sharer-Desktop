import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils import public_func


current_changeLog = ""


def match_current_changeLog() -> None:
    print("Match current changelog from CHANGELOG.md...")
    global current_changeLog
    changeLog_path = os.path.join(BASE_DIR, "CHANGELOG.md")
    product_version = public_func.generate_product_version()
    with open(changeLog_path, "r", encoding="utf-8") as f:
        start = False
        for line in f.readlines():
            if product_version in line:
                start = True
            elif re.findall(r"## \[\d\.\d\.\d\]", line):
                break
            if start:
                current_changeLog += line
    current_changeLog = current_changeLog.rstrip()


def write_current_changeLog() -> None:
    print("Write current changelog to file...")
    result_file = "current_change_log.md"
    result_path = os.path.join(BASE_DIR, result_file)
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(current_changeLog)


if __name__ == "__main__":
    match_current_changeLog()
    write_current_changeLog()
