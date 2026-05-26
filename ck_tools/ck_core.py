# ck_core.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-05-26
# Version: 4.1.0
# Description: CK 构建工具核心流程封装

import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .ck_config_gen import generate_config
from .ck_version import update_ck_version_h


# =========================================================
# Kconfig 配置项名称
# =========================================================

KCONFIG_SYMBOL_CK_TOOLS_ROOT = "CK_TOOLS_ROOT"
KCONFIG_SYMBOL_CK_WORKSPACE_ROOT = "CK_WORKSPACE_ROOT"
KCONFIG_SYMBOL_CK_BUILD_DIR = "CK_BUILD_DIR"
KCONFIG_SYMBOL_CK_CMD_CONFIGURE = "CK_CMD_CONFIGURE"
KCONFIG_SYMBOL_CK_CMD_BUILD = "CK_CMD_BUILD"
KCONFIG_SYMBOL_CK_CMD_CLEAN = "CK_CMD_CLEAN"
KCONFIG_SYMBOL_CK_VERSION_ENABLE = "CK_VERSION_ENABLE"


# =========================================================
# 通用工具函数
# =========================================================

def _split_command(cmd_text):
    """将 Kconfig 中的命令字符串拆分为命令列表。"""
    if not cmd_text:
        raise ValueError("Empty command from Kconfig")
    return shlex.split(cmd_text)


def _kconfig_enabled(value):
    """判断 Kconfig 配置项是否启用。"""
    if value is None:
        return False

    normalized = str(value).strip().lower()
    return normalized not in {"", "n", "false", "0", "off"}


def _resolve_kconfig_path(project_dir, path_text):
    """将 Kconfig 中读取到的路径解析为绝对路径。"""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (Path(project_dir) / path).resolve()


def run_subprocess(cmd_list, cwd=None, capture_output=True):
    """执行子进程，并逐行返回输出。"""
    try:
        process = subprocess.Popen(
            cmd_list,
            cwd=str(cwd) if cwd else None,
            shell=False,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as exc:
        yield f"Error: {exc}"
        raise

    if capture_output and process.stdout:
        for line in process.stdout:
            yield line.rstrip("\n")

    returncode = process.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd_list)


# =========================================================
# Kconfig 读取
# =========================================================

def _load_kconfig(project_dir, kconfig_path, config_path):
    """加载工程 Kconfig 和 .config。"""
    os.environ["srctree"] = str(project_dir)
    os.environ["KCONFIG_CONFIG"] = str(config_path)

    try:
        import kconfiglib
    except ImportError as exc:
        raise RuntimeError("kconfiglib is required to load Kconfig") from exc

    kconf = kconfiglib.Kconfig(str(kconfig_path))
    if config_path.exists():
        kconf.load_config(str(config_path))

    return kconf


def _get_symbol_value(kconf, name, default=None):
    """从 Kconfig 中读取指定配置项的字符串值。"""
    sym = kconf.syms.get(name)
    if sym is None:
        if default is not None:
            return default
        raise KeyError(f"Kconfig symbol not found: {name}")

    value = sym.str_value
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Kconfig symbol has no value: {name}")

    return value


# =========================================================
# 构建上下文
# =========================================================

@dataclass
class CKContext:
    """CK 构建上下文，供核心流程和用户钩子共享。"""

    project_dir: Path
    logger: object = print
    py_path: str = sys.executable

    kconfig_path: Path = field(init=False)
    config_path: Path = field(init=False)
    cmake_config_path: Path = field(init=False)
    header_config_path: Path = field(init=False)

    ck_tools_root: Path = None
    ck_workspace_root: Path = None
    ck_build_dir: Path = None

    ck_cmd_configure: str = ""
    ck_cmd_build: str = ""
    ck_cmd_clean: str = ""
    ck_version_enable: str = "n"

    def __post_init__(self):
        self.project_dir = Path(self.project_dir).resolve()
        self.kconfig_path = self.project_dir / "Kconfig"
        self.config_path = self.project_dir / ".config"
        self.cmake_config_path = self.project_dir / "ck_config.cmake"
        self.header_config_path = self.project_dir / "ck_config.h"

    @property
    def tools_root(self):
        """兼容旧命名：工具根目录。"""
        return self.ck_tools_root

    @property
    def workspace_root(self):
        """兼容旧命名：工作区根目录。"""
        return self.ck_workspace_root

    @property
    def build_dir(self):
        """兼容旧命名：构建目录。"""
        return self.ck_build_dir


# =========================================================
# 用户钩子基类
# =========================================================

class CKHooks:
    """用户钩子基类，工程侧通过继承该类插入自定义流程。"""

    def before_config(self, ctx):
        pass

    def after_config(self, ctx):
        pass

    def before_config_gen(self, ctx):
        pass

    def after_config_gen(self, ctx):
        pass

    def before_build(self, ctx):
        pass

    def after_build(self, ctx):
        pass

    def before_make(self, ctx):
        pass

    def after_make(self, ctx):
        pass

    def before_clean(self, ctx):
        pass

    def after_clean(self, ctx):
        pass

    def on_error(self, ctx, error):
        pass


# =========================================================
# CK 核心流程
# =========================================================

class CKTool:
    """CK 构建工具核心流程。"""

    def __init__(self, project_dir, hooks=None, logger=print):
        self.logger = logger
        self.hooks = hooks or CKHooks()
        self.ctx = CKContext(project_dir=project_dir, logger=logger)
        self.load_kconfig_globals()

    # -----------------------------------------------------
    # Kconfig 配置读取
    # -----------------------------------------------------

    def load_kconfig_globals(self):
        """从 Kconfig 和 .config 中读取全局配置。"""
        kconf = _load_kconfig(
            project_dir=self.ctx.project_dir,
            kconfig_path=self.ctx.kconfig_path,
            config_path=self.ctx.config_path,
        )

        self.ctx.ck_tools_root = _resolve_kconfig_path(
            self.ctx.project_dir,
            _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_TOOLS_ROOT),
        )
        self.ctx.ck_workspace_root = _resolve_kconfig_path(
            self.ctx.project_dir,
            _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_WORKSPACE_ROOT),
        )
        self.ctx.ck_build_dir = _resolve_kconfig_path(
            self.ctx.project_dir,
            _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_BUILD_DIR, "build"),
        )
        self.ctx.ck_cmd_configure = _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_CMD_CONFIGURE)
        self.ctx.ck_cmd_build = _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_CMD_BUILD)
        self.ctx.ck_cmd_clean = _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_CMD_CLEAN)
        self.ctx.ck_version_enable = _get_symbol_value(kconf, KCONFIG_SYMBOL_CK_VERSION_ENABLE, "n")

    # -----------------------------------------------------
    # 固定流程：配置
    # -----------------------------------------------------

    def config(self, auto=False):
        """执行配置流程：menuconfig + 配置文件生成。"""
        self.hooks.before_config(self.ctx)

        self.logger("Executing config operation...")
        self._run_menuconfig()
        self.load_kconfig_globals()
        self.generate_config_files()

        self.hooks.after_config(self.ctx)

        if auto:
            self.build(auto=True)

    def _run_menuconfig(self):
        """启动 menuconfig。"""
        try:
            import kconfiglib
            import menuconfig
        except ImportError as exc:
            raise RuntimeError("kconfiglib and menuconfig are required to run config") from exc

        os.environ["srctree"] = str(self.ctx.project_dir)
        os.environ["KCONFIG_CONFIG"] = str(self.ctx.config_path)

        kconf = kconfiglib.Kconfig(str(self.ctx.kconfig_path))
        menuconfig.menuconfig(kconf)

    def generate_config_files(self):
        """生成 ck_config.cmake 和 ck_config.h。"""
        self.hooks.before_config_gen(self.ctx)

        generate_config(
            config_file=self.ctx.config_path,
            cmake_file=self.ctx.cmake_config_path,
            header_file=self.ctx.header_config_path,
            logger=self.logger,
        )

        self.hooks.after_config_gen(self.ctx)

    # -----------------------------------------------------
    # 固定流程：构建配置
    # -----------------------------------------------------

    def build(self, auto=False):
        """执行构建配置流程：清理构建目录并运行 CMake configure。"""
        self.hooks.before_build(self.ctx)

        self.logger("Executing build operation...")
        if self.ctx.ck_build_dir.exists():
            self.logger("Deleting existing build directory...")
            shutil.rmtree(self.ctx.ck_build_dir)

        self.ctx.ck_build_dir.mkdir(parents=True, exist_ok=True)

        build_cmd = _split_command(self.ctx.ck_cmd_configure)
        self.logger(f"Running: {' '.join(build_cmd)}")
        for line in run_subprocess(build_cmd, cwd=self.ctx.project_dir):
            self.logger(line)

        self.hooks.after_build(self.ctx)

        if auto:
            self.make()

    # -----------------------------------------------------
    # 固定流程：编译
    # -----------------------------------------------------

    def make(self):
        """执行编译流程：可选更新版本号并运行构建命令。"""
        self.hooks.before_make(self.ctx)

        if _kconfig_enabled(self.ctx.ck_version_enable):
            update_ck_version_h(
                file_path=self.ctx.header_config_path,
                work_dir=self.ctx.project_dir,
                logger=self.logger,
            )
        else:
            self.logger("Skipping ck_version.py because CK_VERSION_ENABLE is disabled.")

        self.logger("Executing make operation...")
        make_cmd = _split_command(self.ctx.ck_cmd_build)
        self.logger(f"Running: {' '.join(make_cmd)}")
        for line in run_subprocess(make_cmd, cwd=self.ctx.project_dir):
            self.logger(line)

        self.hooks.after_make(self.ctx)

    # -----------------------------------------------------
    # 固定流程：清理
    # -----------------------------------------------------

    def clean(self):
        """执行清理流程。"""
        self.hooks.before_clean(self.ctx)

        self.logger("Executing clean operation...")
        clean_cmd = _split_command(self.ctx.ck_cmd_clean)
        self.logger(f"Running: {' '.join(clean_cmd)}")
        for line in run_subprocess(clean_cmd, cwd=self.ctx.project_dir):
            self.logger(line)

        self.hooks.after_clean(self.ctx)


# =========================================================
# 命令行入口
# =========================================================

def _print_usage():
    """打印命令行帮助。"""
    print("Usage: python ck_tool.py [auto config build make clean help]")


def cli_main(project_dir=None, hooks=None, logger=print, argv=None):
    """工程侧命令行入口。"""
    argv = argv if argv is not None else sys.argv[1:]
    project_dir = Path(project_dir or os.getcwd()).resolve()

    if not argv:
        _print_usage()
        sys.exit(1)

    tool = CKTool(project_dir=project_dir, hooks=hooks, logger=logger)
    cmd = argv[0].lower()

    try:
        if cmd in ["config", "c"]:
            tool.config()
        elif cmd in ["build", "b"]:
            tool.build()
        elif cmd in ["make", "m"]:
            tool.make()
        elif cmd in ["clean", "cl"]:
            tool.clean()
        elif cmd in ["auto", "a"]:
            tool.config(auto=True)
        elif cmd in ["help", "h"]:
            _print_usage()
        else:
            print(f"Invalid command: {cmd}")
            _print_usage()
            sys.exit(1)
    except Exception as exc:
        try:
            tool.hooks.on_error(tool.ctx, exc)
        finally:
            logger(f"Error: {exc}")
            sys.exit(1)
