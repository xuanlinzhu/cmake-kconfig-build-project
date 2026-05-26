# ck_tool.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-05-26
# Version: 4.1.0
# Description: CK 工程构建入口，工程侧只保留用户自定义钩子

import os
import shutil
import sys
from pathlib import Path


# =========================================================
# 工程路径
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent
KCONFIG_PATH = SCRIPT_DIR / "Kconfig"
CONFIG_PATH = SCRIPT_DIR / ".config"


# =========================================================
# Kconfig 启动加载
# =========================================================

def _resolve_kconfig_path(path_text):
    """将 Kconfig 中读取到的路径解析为绝对路径。"""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (SCRIPT_DIR / path).resolve()


def _load_ck_tools_root_from_kconfig():
    """从工程 Kconfig 中读取 CK_TOOLS_ROOT，用于导入 ck_tools。"""
    os.environ["srctree"] = str(SCRIPT_DIR)
    os.environ["KCONFIG_CONFIG"] = str(CONFIG_PATH)

    try:
        import kconfiglib
    except ImportError as exc:
        raise RuntimeError("kconfiglib is required to load CK_TOOLS_ROOT from Kconfig") from exc

    kconf = kconfiglib.Kconfig(str(KCONFIG_PATH))
    if CONFIG_PATH.exists():
        kconf.load_config(str(CONFIG_PATH))

    sym = kconf.syms.get("CK_TOOLS_ROOT")
    if sym is None or not sym.str_value:
        raise RuntimeError("Kconfig symbol not found: CK_TOOLS_ROOT")

    return _resolve_kconfig_path(sym.str_value)


CK_TOOLS_ROOT = _load_ck_tools_root_from_kconfig()
sys.path.insert(0, str(CK_TOOLS_ROOT))

from ck_tools.ck_core import CKHooks, cli_main


# =========================================================
# 用户自定义钩子
# =========================================================

class ProjectHooks(CKHooks):
    """工程自定义钩子，用户只需要在这里添加项目私有流程。"""

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
        # 示例：编译完成后复制 bin 文件。默认关闭，需要时取消注释并修改文件名和目标路径。
        # self.copy_bin(ctx, bin_name="lr_project.bin")
        pass

    def before_clean(self, ctx):
        pass

    def after_clean(self, ctx):
        pass

    def copy_bin(self, ctx, bin_name):
        """复制 bin 文件到指定目录，可按项目需求修改。"""
        src = ctx.project_dir / "bin" / bin_name
        if not src.exists():
            ctx.logger(f"{src} not found, skip copy.")
            return

        if os.name == "nt":
            dst = Path("C:/tftpboot") / src.name
        else:
            dst = Path("/home/xxx/tftpboot") / src.name

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        ctx.logger(f"Copied {src} to {dst}")


# =========================================================
# 命令行入口
# =========================================================

if __name__ == "__main__":
    cli_main(project_dir=SCRIPT_DIR, hooks=ProjectHooks())
