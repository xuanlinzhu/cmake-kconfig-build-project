# ck_tool.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Version: 2.0.0
# Description: Unified GUI and CLI tool for building with CMake and Kconfig, supporting Windows/Linux

import os
import shlex
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext


SCRIPT_DIR = Path(__file__).resolve().parent
KCONFIG_PATH = SCRIPT_DIR / "Kconfig"
CONFIG_PATH = SCRIPT_DIR / ".config"
# 兼容未加载 Kconfig 前的基础工具根目录
BOOTSTRAP_TOOLS_ROOT = (SCRIPT_DIR / "../../..").resolve()

# Kconfig globals
CK_TOOLS_ROOT = ""
CK_WORKSPACE_ROOT = ""
CK_CMD_CONFIGURE = ""
CK_CMD_BUILD = ""
CK_CMD_CLEAN = ""
CK_VERSION_ENABLE = ""

PY_PATH = sys.executable


def _tool_root():
    if CK_TOOLS_ROOT:
        return _resolve_kconfig_root(CK_TOOLS_ROOT)
    return BOOTSTRAP_TOOLS_ROOT


def _load_kconfig_globals():
    global CK_TOOLS_ROOT, CK_WORKSPACE_ROOT, CK_CMD_CONFIGURE, CK_CMD_BUILD, CK_CMD_CLEAN, CK_VERSION_ENABLE

    os.environ.setdefault("srctree", str(SCRIPT_DIR))
    os.environ.setdefault("KCONFIG_CONFIG", str(CONFIG_PATH))

    try:
        import kconfiglib
    except ImportError as exc:
        raise RuntimeError("kconfiglib is required to load template/project/stm32_test/Kconfig") from exc

    kconf = kconfiglib.Kconfig(str(KCONFIG_PATH))
    if CONFIG_PATH.exists():
        kconf.load_config(str(CONFIG_PATH))

    def get_symbol_value(name, default=None):
        config_value = _read_config_value(name)
        if config_value is not None:
            return config_value
        sym = kconf.syms.get(name)
        if sym is None:
            if default is not None:
                return default
            raise KeyError(f"Kconfig symbol not found: {name}")
        if sym.user_value is not None:
            return sym.user_value
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


def _read_config_value(name):
    if not CONFIG_PATH.exists():
        return None
    prefix = f"CONFIG_{name}="
    for line in CONFIG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith(prefix):
            continue
        value = line[len(prefix):].strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            return value[1:-1]
        return value
    return None


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

    if capture_output and process.stdout is not None:
        for line in process.stdout:
            yield line.rstrip("\n")

    returncode = process.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd_list)


def _run_python_script(script_name, logger=print):
    script_path = _tool_root() / "ck_tools" / script_name
    logger(f"Executing {script_name} ...")
    subprocess.run([PY_PATH, str(script_path)], check=True, cwd=str(SCRIPT_DIR))


def _run_menuconfig(gui=False):
    menuconfig_root = _tool_root()
    if gui:
        menuconfig_fullpath = menuconfig_root / "tools" / "script" / "menuconfig.py"
    else:
        menuconfig_fullpath = menuconfig_root / "ck_tools" / "menuconfig.py"

    fallback_cmds = [
        [PY_PATH, str(menuconfig_fullpath), "Kconfig"],
        ["menuconfig"],
        ["menuconfig.py"],
    ]

    if gui:
        if os.name == "nt":
            for cmd in fallback_cmds:
                try:
                    powershell_command = " ".join(cmd)
                    powershell_full_command = f"& {{ {powershell_command}; exit }}"
                    subprocess.run(
                        ["cmd", "/c", "start", "/wait", "powershell", "-NoExit", "-Command", powershell_full_command],
                        check=True,
                    )
                    return
                except Exception:
                    continue
            raise RuntimeError("All Windows menuconfig attempts failed.")

        term_prog = os.getenv("TERMINAL") or "x-terminal-emulator"
        for cmd in fallback_cmds:
            try:
                subprocess.run([term_prog, "-e", *cmd], check=True)
                return
            except Exception:
                continue
        raise RuntimeError("All Linux menuconfig attempts failed.")

    for cmd in fallback_cmds:
        try:
            subprocess.run(cmd, check=True)
            return
        except Exception:
            continue
    raise RuntimeError("All attempts to run menuconfig failed.")


class CKTool:
    def __init__(self, logger=print):
        self.logger = logger

    def config(self, param=None):
        self.logger("Executing config operation...")
        try:
            _run_menuconfig(gui=False)
            _load_kconfig_globals()
        except Exception as e:
            self.logger(f"Error executing config: {e}")
            sys.exit(1)

        try:
            _run_python_script("ck_config_gen.py", logger=self.logger)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing ck_config_gen.py: {e}")
            sys.exit(1)

        if param in ["auto", "a"]:
            self.build(param)

    def guiconfig(self, param=None):
        self.logger("Executing config operation...")
        try:
            _run_menuconfig(gui=True)
            _load_kconfig_globals()
        except Exception as e:
            self.logger(f"Error executing menuconfig: {e}")
            sys.exit(1)

        try:
            _run_python_script("ck_config_gen.py", logger=self.logger)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing ck_config_gen.py: {e}")
            sys.exit(1)

        if param in ["auto", "a"]:
            self.build(param)

    def build(self, param=None, build_type="Debug"):
        self.logger("Executing build operation...")
        try:
            if shutil.which("cmake") is None:
                raise RuntimeError("cmake not found in PATH")
            if shutil.which("ninja") is None:
                raise RuntimeError("ninja not found in PATH")
            # 交叉编译器检查：只做提示，不强制阻断，避免和 toolchain 文件冲突
            gcc = shutil.which("arm-none-eabi-gcc")
            if gcc:
                self.logger(f"Found ARM GCC: {gcc}")
            else:
                self.logger("Warning: arm-none-eabi-gcc not found in PATH. If toolchain is configured by absolute path, this can be ignored.")

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
        # refresh ck_version.h
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


class CKGui:
    def __init__(self, root):
        self.tool = CKTool(logger=self.print_info)
        self.root = root
        self.root.title("CK-TOOL")
        self.root.geometry(f"720x480+{(self.root.winfo_screenwidth() - 720)//2}+{(self.root.winfo_screenheight()-480)//2}")
        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=80, font=("Microsoft Yahei", 10, "bold"))
        self.output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED, bg="#d7f3e3")
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=15)
        self.add_buttons()
        self.cd_to_script_dir()

    def add_buttons(self):
        btns = {
            "配 置": lambda: self.run(self.tool.guiconfig),
            "构 建": lambda: self.run(self.tool.build),
            "编 译": lambda: self.run(self.tool.make),
            "清 除": lambda: self.run(self.tool.clean),
            # 目前自动会出现问题，导致配置还没结束就直接进行编译
            # "自 动": lambda: self.run(lambda: self.tool.guiconfig("auto")),
        }
        for name, func in btns.items():
            tk.Button(
                self.button_frame,
                text=name,
                command=func,
                padx=20,
                pady=6,
                bg="#d7f3e3",
                font=("Microsoft YaHei", 10, "bold"),
            ).pack(side=tk.LEFT, padx=10)

    def run(self, func):
        threading.Thread(target=func, daemon=True).start()

    def print_info(self, text, error=False):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n", "error" if error else None)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        if error:
            self.output_text.tag_config("error", foreground="red")

    def cd_to_script_dir(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        self.print_info(f"Changed working directory to {script_dir}")


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
        print("Usage: python ck_tool.py [build make clean config auto help]")
    else:
        print(f"Invalid command: {cmd}")
        sys.exit(1)


_load_kconfig_globals()


if __name__ == "__main__":
    cli_main()
