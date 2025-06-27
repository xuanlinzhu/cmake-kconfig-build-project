"""
ck_script.py
zhuxuanlin 2024/5/27
version v1.1
"""
import os
import shutil
import subprocess
import sys

py_path = "/usr/bin/python3"
def config_func(param):
    print("Executing config operation...")
    try:
        subprocess.run([py_path, "../../tools/menuconfig.py", "Kconfig"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing menuconfig: {e}")
        sys.exit(1)
    try:
        print("Executing ck_pylib.py .")
        subprocess.run([py_path, "ck_pylib.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing ck_pylib.py: {e}")
        sys.exit(1)
    if param in ["auto", "a"]:
        build_func(param)

def build_func(param):
    print("Executing build operation...")
    try:
        if os.path.exists("build"):
            print("Deleting existing build directory...")
            shutil.rmtree("build")
        print("Creating build directory...")
        os.makedirs("build")
        os.chdir("build")
        print("Running CMake...")
        cmake_generator = "MinGW Makefiles" if os.name == "nt" else "Unix Makefiles"
        subprocess.run(["cmake", "-G", cmake_generator, ".."], check=True)
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        print(f"Error executing CMake: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    if param in ["auto", "a"]:
        make_func()

def make_func():
    print("Executing make operation...")
    try:
        os.chdir("build") 
        print("Running make...")
        subprocess.run(["make","-j4"], check=True)  
        os.chdir("..")  
    except subprocess.CalledProcessError as e:  
        print(f"Error executing make: {e}")
        sys.exit(1)
    except Exception as e:  
        print(f"Unexpected error: {e}")
        sys.exit(1)
"""
    try:
        print("Copy bin to tftp...")
        subprocess.run(["cp bin/lr_project.bin /home/../tftpboot/"], check=True)
    except subprocess.CalledProcessError as e:  
        print(f"Error executing make: {e}")
        sys.exit(1)
    except Exception as e:  
        print(f"Unexpected error: {e}")
        sys.exit(1)    
"""
def clean_func():
    print("Executing clean operation...")
    try:
        os.chdir("build")  
        print("Running make clean...")
        subprocess.run(["make", "clean"], check=True)  
        os.chdir("..")  
    except subprocess.CalledProcessError as e:  
        print(f"Error executing make clean: {e}")
        sys.exit(1)
    except Exception as e:  
        print(f"Unexpected error: {e}")
        sys.exit(1)

def help_func():
    print("Displays help information...")
    print("Usage: python ck_script.py [ build make clean config auto help ]")
    print("- auto     (a) : Perform auto operation.")
    print("- config   (cn): Perform config operation.")
    print("- build    (b) : Perform build operation.")
    print("- make     (m) : Perform make operation.")
    print("- clean    (cl): Perform clean operation.")
    print("- help     (h) : Display this help message.")

def main():
    if len(sys.argv) < 2:
        print("Please input one parameter [ build make clean config auto help ].")
        sys.exit(1)
    param = sys.argv[1].lower()
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
        print(f"Invalid parameter: {param}, please input build make clean config auto help.")
        sys.exit(1)
    print("ck_script processed.")

if __name__ == "__main__":
    main()
