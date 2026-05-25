# ck_tool.py
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Version: 2.0.0
# Description: Unified GUI and CLI tool for building with CMake and Kconfig, supporting Windows/Linux

import os
import sys
import shutil
import shlex
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext

# Kconfig globals
CK_TOOLS_ROOT = ""
CK_WORKSPACE_ROOT = ""
CK_CMD_CONFIGURE = ""
CK_CMD_BUILD = ""
CK_CMD_CLEAN = ""

# Python path
py_path = sys.executable


def _load_kconfig_globals():
    global CK_TOOLS_ROOT, CK_WORKSPACE_ROOT, CK_CMD_CONFIGURE, CK_CMD_BUILD, CK_CMD_CLEAN

    script_dir = os.path.dirname(os.path.abspath(__file__))
    kconfig_path = os.path.join(script_dir, "Kconfig")
    os.environ.setdefault("srctree", script_dir)
    os.environ.setdefault("KCONFIG_CONFIG", os.path.join(script_dir, ".config"))

    try:
        import kconfiglib
    except ImportError as exc:
        raise RuntimeError("kconfiglib is required to load template/project/test/Kconfig") from exc

    kconf = kconfiglib.Kconfig(kconfig_path)

    def get_symbol_value(name):
        sym = kconf.syms.get(name)
        if sym is None:
            raise KeyError(f"Kconfig symbol not found: {name}")
        return sym.str_value

    CK_TOOLS_ROOT = get_symbol_value("CK_TOOLS_ROOT")
    CK_WORKSPACE_ROOT = get_symbol_value("CK_WORKSPACE_ROOT")
    CK_CMD_CONFIGURE = get_symbol_value("CK_CMD_CONFIGURE")
    CK_CMD_BUILD = get_symbol_value("CK_CMD_BUILD")
    CK_CMD_CLEAN = get_symbol_value("CK_CMD_CLEAN")


def _split_command(cmd_text, fallback_cmd):
    if cmd_text:
        return shlex.split(cmd_text)
    return fallback_cmd


_load_kconfig_globals()


def is_windows():
    return os.name == "nt"

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
        if capture_output:
            for line in process.stdout:
                yield line.strip()
    except Exception as e:
        yield f"Error: {e}"

class CKTool:
    def __init__(self, logger=print):
        self.logger = logger

    def config(self, param=None):
        self.logger("Executing config operation...")

        menuconfig_fullpath = os.path.join(CK_TOOLS_ROOT, "ck_tools", "menuconfig.py")
        fallback_cmds = [
            [py_path, menuconfig_fullpath, "Kconfig"],
            ["menuconfig"],
            ["menuconfig.py"]
        ]
        success = False
        for cmd in fallback_cmds:
            try:
                self.logger(f"Trying to run: {' '.join(cmd)}")
                subprocess.run(cmd, check=True)
                success = True
                break
            except Exception as e:
                self.logger(f"Command failed: {' '.join(cmd)}, error: {e}")

        if not success:
            self.logger("All attempts to run menuconfig failed.")
            sys.exit(1)

        self.logger("Executing ck_pylib.py ...")
        try:
            subprocess.run([py_path, os.path.join(CK_TOOLS_ROOT, "ck_tools", "ck_pylib.py")], check=True)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing ck_pylib.py: {e}")

        if param in ["auto", "a"]:
            self.build(param)


    def guiconfig(self, param=None):
        self.logger("Executing config operation...")

        menuconfig_fullpath = os.path.join(CK_TOOLS_ROOT, "ck_tools", "menuconfig.py")
        fallback_cmds = [
            [py_path, menuconfig_fullpath, "Kconfig"],
            ["menuconfig"],
            ["menuconfig.py"]
        ]
        try:
            if os.name == 'nt':
                for cmd in fallback_cmds:
                    try:
                        powershell_command = ' '.join(cmd)
                        powershell_full_command = f'& {{ {powershell_command}; exit }}'
                        self.logger(f"Trying Windows fallback command: {powershell_full_command}")

                        # 用 cmd /c start /wait 打开新窗口并阻塞，等待关闭
                        subprocess.run([
                            'cmd', '/c', 'start', '/wait', 'powershell',
                            '-NoExit', '-Command', powershell_full_command
                        ], check=True)
                        break
                    except Exception as e:
                        self.logger(f"Windows fallback command failed: {' '.join(cmd)}, error: {e}")
                else:
                    self.logger("All Windows menuconfig attempts failed.")
                    sys.exit(1)
            else:
                term_prog = os.getenv("TERMINAL") or "x-terminal-emulator"
                for cmd in fallback_cmds:
                    try:
                        self.logger(f"Trying Linux fallback command: {term_prog} -e {' '.join(cmd)}")
                        # 确保cmd是列表，这里不用split，用cmd本身是列表
                        subprocess.run([term_prog, "-e", *cmd], check=True)
                        break
                    except Exception as e:
                        self.logger(f"Linux fallback command failed: {' '.join(cmd)}, error: {e}")
                else:
                    self.logger("All Linux menuconfig attempts failed.")
                    sys.exit(1)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing menuconfig: {e}")
            sys.exit(1)

        # 这里是menuconfig执行完毕后才会继续执行
        self.logger("Executing ck_pylib.py ...")
        try:
            subprocess.run([py_path, os.path.join(CK_TOOLS_ROOT, "ck_tools", "ck_pylib.py")], check=True)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing ck_pylib.py: {e}")

        if param in ["auto", "a"]:
            self.build(param)


    def build(self, param=None):
        self.logger("Executing build operation...")
        try:
            if os.path.exists("build"):
                self.logger("Deleting existing build directory...")
                shutil.rmtree("build")

            os.makedirs("build", exist_ok=True)
            build_cmd = _split_command(CK_CMD_CONFIGURE, ["cmake", "-S", ".", "-B", "build", "-G", "Ninja"])
            self.logger(f"Running: {' '.join(build_cmd)}")
            for line in run_subprocess(build_cmd):
                self.logger(line)
        except Exception as e:
            self.logger(f"Error executing build: {e}")

        if param in ["auto", "a"]:
            self.make()

    def make(self):

        # refresh ck_version.h
        self.logger("Executing ck_version.py ...")
        try:
            subprocess.run([py_path, os.path.join(CK_TOOLS_ROOT, "ck_tools", "ck_version.py")], check=True)
        except subprocess.CalledProcessError as e:
            self.logger(f"Error executing ck_version.py: {e}")

        self.logger("Executing make operation...")
        try:
            make_cmd = _split_command(CK_CMD_BUILD, ["cmake", "--build", "build", "-j4"])
            self.logger(f"Running: {' '.join(make_cmd)}")
            for line in run_subprocess(make_cmd):
                self.logger(line)
        except Exception as e:
            self.logger(f"Error executing make: {e}")

    def clean(self):
        self.logger("Executing clean operation...")
        try:
            clean_cmd = _split_command(CK_CMD_CLEAN, ["cmake", "--build", "build", "--target", "clean"])
            self.logger(f"Running: {' '.join(clean_cmd)}")
            for line in run_subprocess(clean_cmd):
                self.logger(line)
        except Exception as e:
            self.logger(f"Error executing clean: {e}")

    def copy_bin(self):
        src = "bin/lr_project.bin"
        if not os.path.exists(src):
            self.logger(f"{src} not found, skip copy.")
            return
        try:
            if is_windows():
                dst = "C:\\tftpboot\\"
                subprocess.run(["copy", src, dst], shell=True)
            else:
                dst = "/home/xxx/tftpboot/"  # 修改为实际路径
                subprocess.run(["cp", src, dst], check=True)
            self.logger(f"Copied {src} to {dst}")
        except Exception as e:
            self.logger(f"Copy failed: {e}")

class CKGui:
    def __init__(self, root):
        self.tool = CKTool(logger=self.print_info)
        self.root = root
        self.root.title("CK-TOOL")
        self.root.geometry(f"720x480+{(self.root.winfo_screenwidth() - 720)//2}+{(self.root.winfo_screenheight()-480)//2}")
        self.output_text = scrolledtext.ScrolledText(root,wrap=tk.WORD,height=20,width= 80,font=("Microsoft Yahei",10,"bold"))
        self.output_text.pack(padx = 10,pady=10,fill=tk.BOTH,expand=True)
        self.output_text.config(state=tk.DISABLED,bg="#d7f3e3")
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
            tk.Button(self.button_frame, text=name, command=func, padx=20, pady=6, bg="#d7f3e3",
                      font=("Microsoft YaHei", 10, "bold")).pack(side=tk.LEFT, padx=10)

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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_main()
    else:
        root = tk.Tk()
        app = CKGui(root)
        root.mainloop()
