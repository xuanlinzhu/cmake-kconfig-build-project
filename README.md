# cmake-kconfig-build-project

## 📌 项目介绍

本项目为中大型工程提供了一个通用的构建模板，实现 **CMake 与 Kconfig 的协同工作机制**。通过 Kconfig 配置生成关键参数宏，驱动 CMake 构建流程，同时生成的宏也可被代码直接使用，实现配置-构建-代码的联动闭环。

## 🏗️ 软件架构

- 基于 CMake 的模块化构建体系。
- 基于 Kconfig 的参数配置界面，支持交互式选择功能模块。
- 自动生成宏定义，用于控制源码编译与功能开关。
- 支持模块化 (`module_template`) 与递归式 (`list_template`) 两种组织方式。

---

# CK-TOOL 使用说明文档

---

## 概述

`ck_tool.py` 是一个基于 Python 开发的跨平台构建辅助工具，集成了对 CMake 和 Kconfig 的统一管理和调用。  
支持命令行（CLI）和图形界面（GUI）两种模式，适用于 Windows 和 Linux 系统。

本工具主要实现：

- 自动化执行项目配置（基于 Kconfig）
- 构建系统生成（基于 CMake）
- 项目编译（调用 Make）
- 构建产物清理
- 支持图形化界面实时查看日志和执行操作

---
## 命令行模式（CLI）入口


---

## 典型使用流程

### CLI 方式
在windows下执行如果使用python不行，就使用python.exe\
linux可以使用python3 \
目的都是调用ck_tool.py这个脚本

```bash
# 进入GUI
python ck_tool.py 

# 配置项目
python ck_tool.py config

# 生成构建系统
python ck_tool.py build

# 编译项目
python ck_tool.py make

# 清理构建产物
python ck_tool.py clean

# 一键自动配置、构建和编译
python ck_tool.py auto
```

- 通过命令行参数执行对应功能  
- 支持命令及简写如下：

| 命令      | 作用           | 简写  |
| --------- | -------------- | ----- |
| config    | 运行配置       | c     |
| build     | 生成构建系统   | b     |
| make      | 编译项目       | m     |
| clean     | 清理构建产物   | cl    |
| auto      | 配置 + 构建 + 编译 | a  |
| help      | 显示帮助信息   | h     |

- 错误命令会打印错误信息并退出


## 📚 CMake API 文档

📂 路径与文件查找函数\
🔍 源文件\
find_current_source_file([var_name])
查找当前目录下 .c/.cpp/.S/.s 文件，加入 ALL_CODE_SOURCES。

find_recurse_source_file([var_name])
递归查找子目录下源文件。

add_some_source_file(file1.c file2.c ...)
手动添加源文件，相对当前目录。

remove_some_source_file(file1.c file2.c ...)
从源文件列表中移除指定文件。

📁 头文件路径 \
find_current_header_dir([var_name])
检查当前目录是否包含 .h，添加至 ALL_CODE_INCLUDES。

find_recurse_header_dir([var_name])
递归查找所有头文件所在路径。

add_some_header_dir(dir1 dir2 ...)
手动添加包含路径。

📚 静态库\
find_current_library_file([var_name])
查找当前目录下 .a 文件。

find_recurse_library_file([var_name])
递归查找所有静态库文件。

add_some_library_file(file1.a file2.a ...)
手动添加库文件。

🔧 模块化构建函数\
set_external_path(PATH BINARY_NAME)
添加外部源码路径作为子项目。

find_cmakelists_current_dir([exclude1 exclude2 ...])
查找一级子目录中包含 CMakeLists.txt 的路径（可排除）。

🧱 构建模板函数\
list_template([flag])
适用于单体项目结构。
module_template([flag])
适用于模块化项目结构。自动调用以下函数：

📤 信息打印函数\
print_all_code_sources([var_name])
打印并返回所有源文件。

print_all_code_includes([var_name])
打印并返回所有头文件路径。

print_all_code_librarys([var_name])
打印并返回所有静态库路径。
