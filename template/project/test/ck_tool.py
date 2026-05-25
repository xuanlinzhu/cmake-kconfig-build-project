# ck_tool.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Version: 2.0.0
# Description: CLI tool for building with CMake and Kconfig

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
KCONFIG_PATH = SCRIPT_DIR / "Kconfig"
CONFIG_PATH = SCRIPT_DIR / ".config"

# Kconfig globals
CK_TOOLS_ROOT = ""
CK_WORKSPACE_ROOT = ""
CK_CMD_CONFIGURE = ""
CK_CMD_BUILD = ""
CK_CMD_CLEAN = ""
CK_VERSION_ENABLE = ""

# Python path
PY_PATH = sys.executable


def _load_kconfig_globals():
    global CK_TOOLS_ROOT, CK_WORKSPACE_ROOT, CK_CMD_CONFIGURE, CK_CMD_BUILD, CK_CMD_CLEAN, CK_VERSION_ENABLE

    os.environ.setdefault("srctree", str(SCRIPT_DIR))
    os.environ.setdefault("KCONFIG_CONFIG", str(CONFIG_PATH))

    try:
        import kconfiglib
    except ImportError as exc:
        raise RuntimeError("kconfiglib is required to load template/project/test/Kconfig") from exc

    kconf = kconfiglib.Kconfig(str(KCONFIG_PATH))
    if CONFIG_PATH.exists():
        kconf.load_config(str(CONFIG_PATH))

    def get_symbol_value(name, default=None):
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

    CK_TOOLS_ROOT = get_symbol_value("CK_TOOLS_ROOT")
    CK_WORKSPACE_ROOT = get_symbol_value("CK_WORKSPACE_ROOT")
    CK_CMD_CONFIGURE = get_symbol_value("CK_CMD_CONFIGURE")
    CK_CMD_BUILD = get_symbol_value("CK_CMD_BUILD")
    CK_CMD_CLEAN = get_symbol_value("CK_CMD_CLEAN")
    CK_VERSION_ENABLE = get_symbol_value("CK_VERSION_ENABLE", "n")


def _resolve_kconfig_root(path_text):
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (SCRIPT_DIR / path).resolve()


def _split_command(cmd_text):
    if not cmd_text:
        raise ValueError("Empty command from Kconfig")
    return shlex.split(cmd_text)


def _kconfig_enabled(value):
    if value is None:
        return False
    normalized = str(value).strip().lower()
    return normalized not in {"", "n", "false", "0", "off"}


def run_subprocess(cmd_list, cwd=None, capture_output=True):
    try:
        process = subprocess.Popen(
            cmd_list,
            cwd=cwd,
            shell=False,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
    except Exception as e:
        yield f"Error: {e}"
        raise

    if capture_output:
        for line in process.stdout:
            yield line.rstrip("\n")

    returncode = process.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd_list)


def _run_python_script(script_name, logger=print):
    script_path = _resolve_kconfig_root(CK_TOOLS_ROOT) / "ck_tools" / script_name
    logger(f"Executing {script_name} ...")
    subprocess.run([PY_PATH, str(script_path)], check=True, cwd=str(SCRIPT_DIR))


def _run_menuconfig():
    import kconfiglib
    import menuconfig

    kconf = kconfiglib.Kconfig(str(KCONFIG_PATH))
    menuconfig.menuconfig(kconf)


class CKTool:
    def __init__(self, logger=print):
        self.logger = logger

    def config(self, param=None):
        self.logger("Executing config operation...")
        try:
            _run_menuconfig()
            _load_kconfig_globals()
        except Exception as e:
            self.logger(f"Error executing config: {e}")
            sys.exit(1)

        try:
            _run_python_script("ck_pylib.py", logger=self.logger)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing ck_pylib.py: {e}")
            sys.exit(1)

        if param in ["auto", "a"]:
            self.build(param)

    def build(self, param=None):
        self.logger("Executing build operation...")
        try:
            build_dir = SCRIPT_DIR / "build"
            if build_dir.exists():
                self.logger("Deleting existing build directory...")
                shutil.rmtree(build_dir)

            build_dir.mkdir(parents=True, exist_ok=True)
            build_cmd = _split_command(CK_CMD_CONFIGURE)
            self.logger(f"Running: {' '.join(build_cmd)}")
            for line in run_subprocess(build_cmd, cwd=str(SCRIPT_DIR)):
                self.logger(line)
        except Exception as e:
            self.logger(f"Error executing build: {e}")
            sys.exit(1)

        if param in ["auto", "a"]:
            self.make()

    def make(self):
        if _kconfig_enabled(CK_VERSION_ENABLE):
            try:
                _run_python_script("ck_version.py", logger=self.logger)
            except subprocess.CalledProcessError as e:
                self.logger(f"Error executing ck_version.py: {e}")
                sys.exit(1)
        else:
            self.logger("Skipping ck_version.py because CK_VERSION_ENABLE is disabled.")

        self.logger("Executing make operation...")
        try:
            make_cmd = _split_command(CK_CMD_BUILD)
            self.logger(f"Running: {' '.join(make_cmd)}")
            for line in run_subprocess(make_cmd, cwd=str(SCRIPT_DIR)):
                self.logger(line)
        except Exception as e:
            self.logger(f"Error executing make: {e}")
            sys.exit(1)

    def clean(self):
        self.logger("Executing clean operation...")
        try:
            clean_cmd = _split_command(CK_CMD_CLEAN)
            self.logger(f"Running: {' '.join(clean_cmd)}")
            for line in run_subprocess(clean_cmd, cwd=str(SCRIPT_DIR)):
                self.logger(line)
        except Exception as e:
            self.logger(f"Error executing clean: {e}")
            sys.exit(1)

    def copy_bin(self):
        src = SCRIPT_DIR / "bin" / "lr_project.bin"
        if not src.exists():
            self.logger(f"{src} not found, skip copy.")
            return
        try:
            if os.name == "nt":
                dst = Path("C:/tftpboot") / src.name
            else:
                dst = Path("/home/xxx/tftpboot") / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            self.logger(f"Copied {src} to {dst}")
        except Exception as e:
            self.logger(f"Copy failed: {e}")


def cli_main():
    tool = CKTool()
    if len(sys.argv) < 2:
        print("Usage: python ck_tool.py [build make clean config auto help]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd in ["config", "c"]:
        tool.config()
    elif cmd in ["build", "b"]:
        tool.build()
    elif cmd in ["make", "m"]:
        tool.make()
    elif cmd in ["clean", "cl"]:
        tool.clean()
    elif cmd in ["auto", "a"]:
        tool.config("auto")
    elif cmd in ["help", "h"]:
        print("Usage: python ck_tool.py [auto config build make clean help]")
    else:
        print(f"Invalid command: {cmd}")
        sys.exit(1)


_load_kconfig_globals()


if __name__ == "__main__":
    cli_main()
