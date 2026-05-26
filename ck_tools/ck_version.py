# ck_version.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-05-26
# Version: 2.2.0
# Description: 根据 Git 提交信息更新 CK 软件版本信息

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path


# =========================================================
# 脚本配置
# =========================================================

CK_VERSION_SCRIPT_VERSION = "2.2.0"


# =========================================================
# Git 信息读取
# =========================================================

def get_git_commit_info(work_dir=None, logger=print):
    """获取当前 Git 仓库的短提交哈希。"""
    try:
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(work_dir) if work_dir else None,
            stderr=subprocess.STDOUT,
        )
        return commit_hash.strip().decode("utf-8")
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode("utf-8", errors="replace") if exc.output else str(exc)
        logger(f"Error retrieving git information: {output.strip()}")
        return None
    except FileNotFoundError:
        logger("Error retrieving git information: git command not found")
        return None


# =========================================================
# 版本信息读取
# =========================================================

def read_version_from_file(file_path, logger=print):
    """从 ck_config.h 中读取版本号和上一次提交哈希。"""
    file_path = Path(file_path)

    if not file_path.exists():
        logger(f"Version file not found: {file_path}")
        return None

    content = file_path.read_text(encoding="utf-8")

    version_match = re.search(r'#define\s+CK_SOFTWARE_VERSION\s+"(\d+\.\d+\.\d+)"', content)
    commit_hash_match = re.search(r'#define\s+CK_SOFTWARE_COMMIT_HASH\s+"([a-fA-F0-9]+)"', content)

    if not version_match or not commit_hash_match:
        logger("Version or commit hash not found in the file.")
        return None

    version = version_match.group(1)
    commit_hash = commit_hash_match.group(1)
    major, minor, patch = map(int, version.split("."))

    return major, minor, patch, commit_hash


# =========================================================
# 版本信息更新
# =========================================================

def _replace_macro_line(line, macro, value):
    """替换指定宏定义行。"""
    if re.match(rf"#define\s+{macro}\b", line):
        return f'#define {macro} "{value}"\n'
    return line


def update_ck_version_h(file_path="ck_config.h", work_dir=None, logger=print):
    """按照既定版本策略更新 ck_config.h 中的版本信息。"""
    file_path = Path(file_path)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_commit_hash = get_git_commit_info(work_dir=work_dir, logger=logger)

    if not current_commit_hash:
        logger("Failed to retrieve commit hash.")
        return False

    version_info = read_version_from_file(file_path, logger=logger)
    if not version_info:
        logger("Failed to determine version and commit hash from the file.")
        return False

    major, minor, patch, last_commit_hash = version_info

    # 版本策略：提交哈希变化时 minor 加一并清零 patch；提交哈希不变时 patch 加一。
    if current_commit_hash != last_commit_hash:
        minor += 1
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)

    updated_lines = []
    for line in lines:
        line = _replace_macro_line(line, "CK_SOFTWARE_VERSION", new_version)
        line = _replace_macro_line(line, "CK_SOFTWARE_BUILD_TIME", current_time)
        line = _replace_macro_line(line, "CK_SOFTWARE_COMMIT_HASH", current_commit_hash)
        updated_lines.append(line)

    file_path.write_text("".join(updated_lines), encoding="utf-8", newline="\n")

    logger(
        f"Updated {file_path} with version {new_version}, "
        f"build time {current_time}, commit hash {current_commit_hash}"
    )
    return True


# =========================================================
# 命令行入口
# =========================================================

def main(argv=None):
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="Update CK software version macros")
    parser.add_argument("--header", default="ck_config.h", help="Input and output ck_config.h file")
    parser.add_argument("--work-dir", default=".", help="Git working directory")
    args = parser.parse_args(argv)

    update_ck_version_h(
        file_path=args.header,
        work_dir=args.work_dir,
    )


if __name__ == "__main__":
    main()
