# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2024-11-20
# Version: 1.0

# Description: This file is used to display a graphy for using CMake and Kconfig.

import os
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import shutil
import threading

class ck_gui_entry:
    def __init__(self,root):
        self.root = root
        self.root.title("CK_GUI")
        self.root.geometry(f"720x480+{(self.root.winfo_screenwidth() - 720)//2}+{(self.root.winfo_screenheight()-480)//2}")
        self.output_text = scrolledtext.ScrolledText(root,wrap=tk.WORD,height=20,width= 80,font=("Microsoft Yahei",10,"bold"))
        self.output_text.pack(padx = 10,pady=10,fill=tk.BOTH,expand=True)
        self.output_text.config(state=tk.DISABLED,bg="#d7f3e3")

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady= 20)

        self.add_command_buttons()

        self.cd_path()

    def add_command_buttons(self):
        buttons = {
            "配 置":self.config_task,
            "构 建":self.build_task,
            "编 译":self.make_task,
            "清 除":self.clean_task,
            "自 动":self.auto_task,
        }
        for name,func in buttons.items():
            btn = tk.Button(self.button_frame,text=name,command=func,padx=25,pady=8,bg="#d7f3e3",font=("Microsoft Yahei",10,"bold"))
            btn.pack(side=tk.LEFT,padx=15)

    def auto_task(self):
        threading.Thread(target=self.auto_func,daemon=True).start()

    def auto_func(self):
        self.config_func()
        self.build_func()
        self.make_func()


    def clean_task(self):
        threading.Thread(target=self.clean_func,daemon=True).start()

    def clean_func(self):
        self.print_info("Executing clean operation...")
        try:
            os.chdir("build")  
            self.print_info("Running make clean...")
            process = subprocess.Popen(["make", "clean"],shell=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding="utf-8")
            for line in process.stdout:
                self.print_info(line)
            os.chdir("..")  
        except subprocess.CalledProcessError as e:  
            self.print_info(f"Error executing make clean: {e}")

        except Exception as e:  
            self.print_info(f"Unexpected error: {e}")



    def make_task(self):
        threading.Thread(target=self.make_func,daemon=True).start()

    def make_func(self):
        self.print_info("Executing make operation...")
        try:
            os.chdir("build") 
            self.print_info("Running make...")
            process = subprocess.Popen(["make","-j4"],shell=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding="utf-8")
            for line in process.stdout:
                self.print_info(line)
            os.chdir("..")  
        except subprocess.CalledProcessError as e:  
            self.print_info(f"Error executing make: {e}")
        except Exception as e:  
            self.print_info(f"Unexpected error: {e}")


    def build_task(self):
        threading.Thread(target=self.build_func,daemon=True).start()

    def build_func(self):
        self.print_info("Executing build operation...")
        try:
            if os.path.exists("build"):
                self.print_info("Deleting existing build directory...")
                shutil.rmtree("build")
            self.print_info("Creating build directory...")
            os.makedirs("build")
            os.chdir("build")
            self.print_info("Running CMake...")
            cmake_generator = "MinGW Makefiles" if os.name == "nt" else "Unix Makefiles"
            process = subprocess.Popen(["cmake", "-G", cmake_generator, ".."],shell=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding="utf-8")
            for line in process.stdout:
                self.print_info(line)
            os.chdir("..")
        except subprocess.CalledProcessError as e:
            self.print_info(f"Error executing CMake: {e}")
        except Exception as e:
            self.print_info(f"Unexpected error: {e}")

    def config_task(self):
        threading.Thread(target=self.config_func,daemon=True).start()


    def config_func(self):
        self.print_info("Executing config operation...")
        try:
            process = subprocess.Popen("guiconfig.exe",shell=True,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding="utf-8")
            for line in process.stdout:
                self.print_info(line)
        except subprocess.CalledProcessError as e:
            self.print_info(f"Error executing menuconfig: {e}")

        try:
            self.print_info("Executing ck_pylib.py .")
            subprocess.run(["python", "ck_pylib.py"], check=True)
        except subprocess.CalledProcessError as e:
            self.print_info(f"Error executing ck_pylib.py: {e}")


   

    def print_info(self,text,error=False):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END,text,"error" if error else None)
        self.output_text.insert(tk.END,"\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        if error:
            self.output_text.tag_config("error",foreground="red")

    def cd_path(self):
        file_path = os.path.abspath(__file__)
        file_dir = os.path.dirname(file_path)

        cur_dir = os.getcwd()

        if file_dir != cur_dir:
            os.chdir(file_dir)
            self.print_info(f"cd path to {file_dir}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ck_gui_entry(root)
    root.mainloop()