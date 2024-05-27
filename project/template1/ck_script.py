"""
ck_script.py
zhuxuanlin 2024/5/27
version v1.1
"""
import os
import shutil
import subprocess
import sys

def config_func(param):
    """
    配置函数：首先尝试运行menuconfig进行配置，接着运行ck_pylib.py脚本。
    如果param参数指定为"auto"或"a"，则会调用build_func函数。
    
    参数:
    param - 一个字符串参数，用于指定配置流程的选项。
    
    返回值:
    无
    """
    print("Executing config operation...")
    # 尝试运行menuconfig，如果不存在则尝试运行menuconfig.py
    try:
        subprocess.run(["menuconfig"], check=True)
    except FileNotFoundError:
        subprocess.run(["menuconfig.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing menuconfig: {e}")
        sys.exit(1)
    
    # 尝试执行ck_pylib.py脚本
    try:
        print("Executing ck_pylib.py .")
        subprocess.run(["python", "ck_pylib.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing ck_pylib.py: {e}")
        sys.exit(1)
    
    # 如果param参数为"auto"或"a"，则调用build_func函数
    if param in ["auto", "a"]:
        build_func(param)

def build_func(param):
    """
    根据给定参数构建工程。
    
    参数:
    param: 字符串，指定构建操作的行为。如果为"auto"或"a"，则自动执行构建。
    
    无返回值。
    """
    print("Executing build operation...")
    try:
        # 检查是否存在名为"build"的目录，如果存在，则删除。
        if os.path.exists("build"):
            print("Deleting existing build directory...")
            shutil.rmtree("build")
        
        # 创建"build"目录。
        print("Creating build directory...")
        os.makedirs("build")
        
        # 进入"build"目录。
        os.chdir("build")
        print("Running CMake...")
        # 根据操作系统选择合适的CMake生成器。
        cmake_generator = "MinGW Makefiles" if os.name == "nt" else "Unix Makefiles"
        subprocess.run(["cmake", "-G", cmake_generator, ".."], check=True)
        # 返回上级目录。
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        # 处理CMake执行过程中返回非零退出码的错误。
        print(f"Error executing CMake: {e}")
        sys.exit(1)
    except Exception as e:
        # 处理其他意外异常。
        print(f"Unexpected error: {e}")
        sys.exit(1)
    
    # 如果参数指定为自动构建，则调用make_func函数进行构建。
    if param in ["auto", "a"]:
        make_func()

def make_func():
    """
    执行make操作的函数。
    该函数尝试更改当前工作目录到"build"，执行make命令，然后返回上级目录。
    如果make命令执行失败，或者过程中发生其他异常，函数将打印错误信息并退出。
    
    参数:
    无
    
    返回值:
    无
    """
    print("Executing make operation...")
    try:
        os.chdir("build")  # 尝试将当前工作目录更改为"build"
        print("Running make...")
        subprocess.run(["make"], check=True)  # 执行make命令，并检查其返回值
        os.chdir("..")  # 将当前工作目录更改回上级目录
    except subprocess.CalledProcessError as e:  # 捕获make命令执行失败的异常
        print(f"Error executing make: {e}")
        sys.exit(1)
    except Exception as e:  # 捕获其他所有异常
        print(f"Unexpected error: {e}")
        sys.exit(1)

def clean_func():
    """
    执行清理操作的函数。
    该函数尝试进入名为“build”的目录，运行“make clean”命令，然后返回上级目录。
    如果“make clean”命令执行失败，或者过程中发生其他异常，函数将打印错误信息并退出。
    
    参数:
    无
    
    返回值:
    无
    """
    print("Executing clean operation...")
    try:
        os.chdir("build")  # 进入build目录
        print("Running make clean...")
        subprocess.run(["make", "clean"], check=True)  # 执行make clean命令
        os.chdir("..")  # 返回上级目录
    except subprocess.CalledProcessError as e:  # 捕获make clean命令执行失败的异常
        print(f"Error executing make clean: {e}")
        sys.exit(1)
    except Exception as e:  # 捕获其他所有异常
        print(f"Unexpected error: {e}")
        sys.exit(1)

def help_func():
    """
    显示帮助信息的函数。
    该函数不接受任何参数，并且没有返回值。
    它主要用于输出有关脚本可用操作的简要帮助信息。

    参数:
    无

    返回值:
    无
    """
    # 打印基本的帮助信息
    print("Displays help information...")
    print("Usage: python ck_script.py [ build make clean config auto help ]")
    # 打印可用的命令选项及其简写
    print("- auto     (a) : Perform auto operation.")
    print("- config   (cn): Perform config operation.")
    print("- build    (b) : Perform build operation.")
    print("- make     (m) : Perform make operation.")
    print("- clean    (cl): Perform clean operation.")
    print("- help     (h) : Display this help message.")

def main():
    """
    主函数，用于解析命令行参数并调用相应的处理函数。
    
    参数:
    - 无
    
    返回值:
    - 无
    """
    # 检查命令行参数数量是否足够
    if len(sys.argv) < 2:
        print("Please input one parameter [ build make clean config auto help ].")
        sys.exit(1)

    # 将命令行参数转换为小写
    param = sys.argv[1].lower()
    # 根据参数调用相应的函数
    if param in ["auto", "a"]:
        config_func(param)
    elif param in ["config", "cn"]:
        config_func(param)
    elif param in ["build", "b"]:
        build_func(param)
    elif param in ["make", "m"]:
        make_func()
    elif param in ["clean", "cl"]:
        clean_func()
    elif param in ["help", "h"]:
        help_func()
    else:
        # 处理无效参数情况
        print(f"Invalid parameter: {param}, please input build make clean config auto help.")
        sys.exit(1)
    
    # 处理完成后的提示信息
    print("ck_script processed.")

if __name__ == "__main__":
    main()
