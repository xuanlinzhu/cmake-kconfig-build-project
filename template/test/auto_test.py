import os
import subprocess
import tkinter as tk
from tkinter import ttk
import time
import threading
import shutil 

# ---------------- 自动切换到脚本所在目录 ----------------

PYTHON_EXECUTABLE = "python" # <-- 修改这里

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
print(f"[INFO] 当前工作目录已切换到脚本目录: {SCRIPT_DIR}")

TESTS_DIR = "."


class TestBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CK Test Tool")

        # 先隐藏窗口，防止闪动
        self.root.withdraw()
        self.root.geometry("480x600")
        self.center_window()  # 启动时居中窗口
        # 设置完毕后显示窗口
        self.root.deiconify()

        self.is_building = False  # 用于停止编译

        # ---------------- 选择编译模式 ----------------
        frame_options = ttk.LabelFrame(root, text="编译选项")
        frame_options.pack(fill="x", padx=10, pady=5)

        self.build_option = tk.StringVar(value="all")  # 默认重新编译
        ttk.Radiobutton(frame_options, text="重新编译", variable=self.build_option, value="all").pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(frame_options, text="增量编译", variable=self.build_option, value="only_missing").pack(side="left", padx=10, pady=5)

        # ---------------- 模块列表 (带滚动条) ----------------
        frame_modules_outer = ttk.LabelFrame(root, text="模块列表")
        frame_modules_outer.pack(fill="both", expand=True, padx=10, pady=5)

        # 1. 创建 Canvas
        self.canvas = tk.Canvas(frame_modules_outer, borderwidth=0)
        
        # 2. 创建 垂直滚动条
        scrollbar = ttk.Scrollbar(frame_modules_outer, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        # 3. 配置 Canvas 使用滚动条
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        # 4. 创建一个 Frame，所有 Checkbutton 都会放在这个 Frame 里
        self.frame_modules = ttk.Frame(self.canvas)
        
        # 5. 将 frame_modules 放入 Canvas 窗口中
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.frame_modules, anchor="nw") 
        
        # 6. 绑定事件：当外部框架大小改变时，同步更新 frame_modules 在 Canvas 中的宽度
        frame_modules_outer.bind('<Configure>', self._on_frame_configure)


        # ---------------- 日志显示 ----------------
        frame_log = ttk.LabelFrame(root, text="编译日志")
        frame_log.pack(fill="both", expand=False, padx=10, pady=5) 
        self.log_text = tk.Text(frame_log, height=6, wrap="none") 
        self.log_text.pack(fill="both", expand=True)

        # ---------------- 进度条 ----------------
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # ---------------- 操作按钮 ----------------
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(fill="x", padx=10, pady=5)

        self.btn_build = ttk.Button(frame_buttons, text="开始编译", command=self.toggle_build)
        self.btn_build.pack(side="left", padx=5)

        ttk.Button(frame_buttons, text="刷新列表", command=self.scan_modules).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="删除编译", command=self.delete_build).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="退出", command=root.quit).pack(side="right", padx=5)

        self.scan_modules()
        
    # --- 新增的滚轮事件处理方法 ---
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件，使 Canvas 滚动"""
        if self.canvas.winfo_exists():
            # 统一处理滚轮单位，兼容 Windows/Linux (event.delta) 和 macOS (event.num)
            if event.delta: # Windows/Linux
                # 滚轮值通常是120的倍数，标准化为1
                delta = event.delta // 120 
            elif event.num != 0: # macOS (使用 Button 4/5 或 event.num)
                # event.num 是 4 或 5，表示向上或向下
                delta = -event.num / 4 # 简易标准化
            else:
                return # 忽略其他事件

            # 滚动 Canvas。yview_scroll(number, what)，number是移动的单位数，what是"units"或"pages"
            self.canvas.yview_scroll(int(-1 * delta), "units")

    def _on_frame_configure(self, event):
        """当外部框架大小改变时，更新 Canvas 内 Frame 的宽度，使其填充 Canvas"""
        # 获取 Canvas 的当前宽度
        canvas_width = event.width
        # 更新 Canvas 内 Frame 的宽度
        self.canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
        # 每次宽度改变后，更新滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def center_window(self):
        """让窗口在屏幕中间显示"""
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.root.geometry(f'+{x}+{y}')

    # ---------------- 删除编译 ----------------
    def delete_build(self):
        selected_modules = [m for m in self.modules if self.module_vars[m].get() == 1]
        if not selected_modules:
            self.log("[WARN] 没有选择模块进行删除")
            return
        for module in selected_modules:
            bin_path = os.path.join(TESTS_DIR, module, "bin")
            build_path = os.path.join(TESTS_DIR, module, "build")
            for path in [bin_path, build_path]:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                        self.log(f"[删除] {module} -> {os.path.basename(path)} 已删除")
                    except Exception as e:
                        self.log(f"[错误] 删除 {module} -> {os.path.basename(path)} 失败: {e}")
        self.scan_modules()  # 删除后刷新列表

    def scan_modules(self):
        # 清除旧的模块列表
        for widget in self.frame_modules.winfo_children():
            # 先解除绑定，避免重复绑定和内存泄漏
            widget.unbind("<MouseWheel>") 
            widget.destroy()

        self.modules = [d for d in os.listdir(TESTS_DIR) if os.path.isdir(os.path.join(TESTS_DIR, d))]
        self.module_vars = {} 
        
        for module in self.modules:
            frame = ttk.Frame(self.frame_modules)
            frame.pack(fill="x", pady=2)

            var = tk.IntVar(value=1)
            self.module_vars[module] = var
            cb = ttk.Checkbutton(frame, text=module, variable=var)
            cb.pack(side="left", anchor="w")

            # 检测状态
            build_dir = os.path.join(TESTS_DIR, module, "build")
            bin_dir = os.path.join(TESTS_DIR, module, "bin")
            build_done = os.path.exists(os.path.join(build_dir, "CTestTestfile.cmake"))
            bin_done = os.path.isdir(bin_dir) and any(os.path.isfile(os.path.join(bin_dir, f)) for f in os.listdir(bin_dir))
            status_ok = build_done and bin_done

            # 使用 Unicode 字符显示状态
            status_label = tk.Label(frame, text="✅" if status_ok else "❌",
                                     font=("Arial", 12),
                                     bg="white",   
                                     fg="green" if status_ok else "red")  
            # 【修改点】使用 padx=20 增加右侧外边距，避开滚动条
            status_label.pack(side="right", padx=30)
            
            # 【滚轮解决方案】绑定滚轮事件到每个模块行和其子控件
            frame.bind("<MouseWheel>", self._on_mousewheel)
            cb.bind("<MouseWheel>", self._on_mousewheel)
            status_label.bind("<MouseWheel>", self._on_mousewheel)

        # 关键步骤：通知 Canvas 重新计算滚动区域大小
        self.frame_modules.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # 绑定滚轮事件到 Canvas 本身和主要的 Frame 
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.frame_modules.bind("<MouseWheel>", self._on_mousewheel)


    def log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def toggle_build(self):
        if not self.is_building:
            self.is_building = True
            self.btn_build.config(text="停止编译")
            # 使用线程防止阻塞界面
            threading.Thread(target=self.start_build, daemon=True).start()
        else:
            self.is_building = False
            self.log("[INFO] 用户请求停止编译")
            self.btn_build.config(text="开始编译")

    def start_build(self):
        selected_modules = [m for m in self.modules if self.module_vars[m].get() == 1]
        total = len(selected_modules)
        if total == 0:
            self.log("[WARN] 没有选择任何模块")
            self.is_building = False
            self.btn_build.config(text="开始编译")
            return

        start_time = time.time()
        for i, module in enumerate(selected_modules, 1):
            if not self.is_building:
                break

            # --- 统一的状态判断标准 (宽松版) ---
            build_dir = os.path.join(TESTS_DIR, module, "build")
            bin_dir = os.path.join(TESTS_DIR, module, "bin")

            build_done = os.path.exists(os.path.join(build_dir, "CTestTestfile.cmake"))
            # 宽松判断：bin 目录下存在任意文件
            bin_done = os.path.isdir(bin_dir) and any(os.path.isfile(os.path.join(bin_dir, f)) for f in os.listdir(bin_dir))
            
            status_ready = build_done and bin_done

            # 检查是否满足增量编译和已就绪的条件
            if self.build_option.get() == "only_missing" and status_ready:
                self.log(f"[跳过] {module} 已编译并就绪 (✅)")
            else:
                self.log(f"[开始] 编译 {module} ...")

                # 先 build
                build_cmd = [PYTHON_EXECUTABLE, "ck_tool.py", "b"]
                try:
                    subprocess.run(build_cmd, cwd=os.path.join(TESTS_DIR, module), check=True)
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    self.log(f"[错误] {module} build 失败: {e}")
                    continue

                # 再 make
                make_cmd = [PYTHON_EXECUTABLE, "ck_tool.py", "m"]
                try:
                    subprocess.run(make_cmd, cwd=os.path.join(TESTS_DIR, module), check=True)
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    self.log(f"[错误] {module} make 失败: {e}")
                    continue

                self.log(f"[完成] {module}")

            # ---------------- 刷新列表并保持选择状态 ----------------
            saved_state = {m: self.module_vars[m].get() for m in self.modules if m in self.module_vars}
            self.scan_modules()
            for m, val in saved_state.items():
                if m in self.module_vars:
                    self.module_vars[m].set(val)

            # 更新进度
            percent = int(i / total * 100)
            elapsed = time.time() - start_time
            remaining = elapsed / i * (total - i) if i > 0 else 0
            self.progress["value"] = percent
            self.log(f"进度: {percent}% 已用: {int(elapsed)}s 预计剩余: {int(remaining)}s")

        self.is_building = False
        self.btn_build.config(text="开始编译")
        self.log("[INFO] 编译结束或已停止")


if __name__ == "__main__":
    root = tk.Tk()
    app = TestBuilderApp(root)
    root.mainloop()