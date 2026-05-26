# ck_config_gen.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-05-26
# Version: 2.2.0
# Description: 根据 Kconfig 生成 CMake 配置文件和 C 头文件

import argparse
import os
import re
from collections import OrderedDict
from pathlib import Path


# =========================================================
# 脚本配置
# =========================================================

CK_CONFIG_GEN_VERSION = "2.2.0"
CONFIG_PREFIX = "CONFIG_"


# =========================================================
# 通用工具函数
# =========================================================

def _remove_config_prefix(key):
    """移除 Kconfig 自动生成的 CONFIG_ 前缀。"""
    if key.startswith(CONFIG_PREFIX):
        return key[len(CONFIG_PREFIX):]
    return key


def _strip_quote(value):
    """移除字符串配置值外层的双引号。"""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _escape_cmake_string(value):
    """转义 CMake 字符串中的特殊字符。"""
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _normalize_header_value(value):
    """将 Kconfig 的值转换为 C 宏可用的值。"""
    value = value.strip()

    if value == "y":
        return "1"
    if value == "n":
        return "0"

    return value


def _is_kconfig_enabled(value):
    """判断 Kconfig 配置项是否启用。"""
    normalized = str(value).strip().lower()
    return normalized not in {"", "n", "false", "0", "off"}


# =========================================================
# .config 解析
# =========================================================

def parse_config_file(config_file):
    """解析 .config 文件，返回有序配置字典。"""
    config_file = Path(config_file)
    config_vars = OrderedDict()

    with config_file.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = _remove_config_prefix(key.strip())
            value = value.strip()
            config_vars[key] = value

    return config_vars


# =========================================================
# 生成文件头
# =========================================================

def _write_cmake_file_header(file):
    """写入 ck_config.cmake 文件头。"""
    file.write("# =========================================================\n")
    file.write("# 文件说明\n")
    file.write("# =========================================================\n")
    file.write("# 本文件由 ck_config_gen.py 自动生成，请勿手动修改。\n")
    file.write("# 生成来源：Kconfig / .config\n")
    file.write(f"# 脚本版本：{CK_CONFIG_GEN_VERSION}\n")
    file.write("# 说明：本文件用于将 Kconfig 配置导出给 CMake 使用。\n")
    file.write("# =========================================================\n\n")


def _write_header_file_header(file):
    """写入 ck_config.h 文件头。"""
    file.write("/*\n")
    file.write(" * =========================================================\n")
    file.write(" * 文件说明\n")
    file.write(" * =========================================================\n")
    file.write(" * 本文件由 ck_config_gen.py 自动生成，请勿手动修改。\n")
    file.write(" * 生成来源：Kconfig / .config\n")
    file.write(f" * 脚本版本：{CK_CONFIG_GEN_VERSION}\n")
    file.write(" *\n")
    file.write(" * 说明：\n")
    file.write(" *   1. 本文件用于将 Kconfig 配置导出给 C/C++ 工程使用。\n")
    file.write(" *   2. 执行 config 或 auto 时，本文件会被重新生成。\n")
    file.write(" *   3. 开启 CK_VERSION_ENABLE 后，版本宏会保留旧值并由 ck_version.py 更新。\n")
    file.write(" * =========================================================\n")
    file.write(" */\n\n")


# =========================================================
# CMake 配置生成
# =========================================================

def write_cmake_file(config_vars, cmake_file):
    """将配置字典写入 ck_config.cmake。"""
    cmake_file = Path(cmake_file)
    cmake_file.parent.mkdir(parents=True, exist_ok=True)

    with cmake_file.open("w", encoding="utf-8", newline="\n") as file:
        _write_cmake_file_header(file)

        for key, value in config_vars.items():
            cmake_value = _escape_cmake_string(_strip_quote(value))
            file.write(f'set({key} "{cmake_value}")\n')


def convert_config_to_cmake(config_file, cmake_file):
    """将 .config 转换为 ck_config.cmake。"""
    config_vars = parse_config_file(config_file)
    write_cmake_file(config_vars, cmake_file)


# =========================================================
# C 头文件生成
# =========================================================

def _read_existing_version_macros(header_file):
    """读取旧 ck_config.h 中已有的版本宏。"""
    header_file = Path(header_file)
    version_macros = {}

    if not header_file.exists():
        return version_macros

    macro_patterns = {
        "CK_SOFTWARE_VERSION": r'#define\s+CK_SOFTWARE_VERSION\s+"(.+)"',
        "CK_SOFTWARE_BUILD_TIME": r'#define\s+CK_SOFTWARE_BUILD_TIME\s+"(.+)"',
        "CK_SOFTWARE_COMMIT_HASH": r'#define\s+CK_SOFTWARE_COMMIT_HASH\s+"(.+)"',
    }

    with header_file.open("r", encoding="utf-8") as file:
        for line in file:
            for macro, pattern in macro_patterns.items():
                match = re.match(pattern, line)
                if match:
                    version_macros[macro] = f'"{match.group(1)}"'

    return version_macros


def _merge_version_macros(config_dict, header_file):
    """根据 CK_VERSION_ENABLE 决定是否合并版本宏。"""
    version_enabled = _is_kconfig_enabled(config_dict.get("CK_VERSION_ENABLE", "0"))

    default_macros = {
        "CK_SOFTWARE_VERSION": '"0.0.1"',
        "CK_SOFTWARE_BUILD_TIME": '"1970-01-01 00:00:00"',
        "CK_SOFTWARE_COMMIT_HASH": '"0000000"',
    }

    if not version_enabled:
        for macro in default_macros:
            config_dict.pop(macro, None)
        return config_dict

    existing_macros = _read_existing_version_macros(header_file)
    default_macros.update(existing_macros)
    config_dict.update(default_macros)
    return config_dict


def write_header_file(config_vars, header_file):
    """将配置字典写入 ck_config.h。"""
    header_file = Path(header_file)
    header_file.parent.mkdir(parents=True, exist_ok=True)

    config_dict = OrderedDict()
    for key, value in config_vars.items():
        config_dict[key] = _normalize_header_value(value)

    config_dict = _merge_version_macros(config_dict, header_file)

    with header_file.open("w", encoding="utf-8", newline="\n") as file:
        _write_header_file_header(file)
        file.write("#ifndef __CK_CONFIG_H__\n")
        file.write("#define __CK_CONFIG_H__\n\n")

        for key in sorted(config_dict.keys()):
            file.write(f"#define {key} {config_dict[key]}\n")

        file.write("\n#endif /* __CK_CONFIG_H__ */\n")


def convert_config_to_header(config_file, header_file):
    """将 .config 转换为 ck_config.h。"""
    config_vars = parse_config_file(config_file)
    write_header_file(config_vars, header_file)


# =========================================================
# 对外接口
# =========================================================

def generate_config(config_file=".config", cmake_file="ck_config.cmake", header_file="ck_config.h", logger=print):
    """生成 CMake 配置文件和 C 头文件。"""
    config_file = Path(config_file)
    cmake_file = Path(cmake_file)
    header_file = Path(header_file)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config_vars = parse_config_file(config_file)
    write_cmake_file(config_vars, cmake_file)
    write_header_file(config_vars, header_file)

    logger(f"Generated {cmake_file}")
    logger(f"Generated {header_file}")


# =========================================================
# 命令行入口
# =========================================================

def main(argv=None):
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="Generate CK config files from Kconfig .config")
    parser.add_argument("--config", default=".config", help="Input .config file")
    parser.add_argument("--cmake", default="ck_config.cmake", help="Output ck_config.cmake file")
    parser.add_argument("--header", default="ck_config.h", help="Output ck_config.h file")
    args = parser.parse_args(argv)

    generate_config(
        config_file=args.config,
        cmake_file=args.cmake,
        header_file=args.header,
    )


if __name__ == "__main__":
    main()
