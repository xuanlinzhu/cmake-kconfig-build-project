# cmake-kconfig-build-project

## 📌 项目介绍

本项目为中大型工程提供了一个通用的构建模板，实现 **CMake 与 Kconfig 的协同工作机制**。通过 Kconfig 配置生成关键参数宏，驱动 CMake 构建流程，同时生成的宏也可被代码直接使用，实现配置-构建-代码的联动闭环。

## 🏗️ 软件架构

- 基于 CMake 的模块化构建体系。
- 基于 Kconfig 的参数配置界面，支持交互式选择功能模块。
- 自动生成宏定义，用于控制源码编译与功能开关。
- 支持模块化 (`module_template`) 与递归式 (`list_template`) 两种组织方式。

---

## 🚀 使用方式


进入工程路径：

```powershell
cd .\project\template\
```

| 操作   | 命令                              |
| ---- | ------------------------------- |
| 配置   | `.\ck_script.bat cn` 或 `config` |
| 构建   | `.\ck_script.bat b` 或 `build`   |
| 编译   | `.\ck_script.bat m` 或 `make`    |
| 清理   | `.\ck_script.bat cl` 或 `clean`  |
| 一键构建 | `.\ck_script.bat a` 或 `auto`    |


## 📚 CMake API 文档
作者： zhuxuanlin \
版本： v1.1 \
更新时间： 2025-06-28 \
描述： 本文档介绍项目中封装的 CMake 宏与函数，用于模块化组织源文件、头文件、库文件等构建资源。

📂 路径与文件查找函数
🔍 源文件
find_current_source_file([var_name])
查找当前目录下 .c/.cpp/.S/.s 文件，加入 ALL_CODE_SOURCES。

find_recurse_source_file([var_name])
递归查找子目录下源文件。

add_some_source_file(file1.c file2.c ...)
手动添加源文件，相对当前目录。

remove_some_source_file(file1.c file2.c ...)
从源文件列表中移除指定文件。

📁 头文件路径
find_current_header_dir([var_name])
检查当前目录是否包含 .h，添加至 ALL_CODE_INCLUDES。

find_recurse_header_dir([var_name])
递归查找所有头文件所在路径。

add_some_header_dir(dir1 dir2 ...)
手动添加包含路径。

📚 静态库
find_current_library_file([var_name])
查找当前目录下 .a 文件。

find_recurse_library_file([var_name])
递归查找所有静态库文件。

add_some_library_file(file1.a file2.a ...)
手动添加库文件。

🔧 模块化构建函数
set_external_path(PATH BINARY_NAME)
添加外部源码路径作为子项目。

find_cmakelists_current_dir([exclude1 exclude2 ...])
查找一级子目录中包含 CMakeLists.txt 的路径（可排除）。

🧱 构建模板函数
list_template([flag])
适用于单体项目结构。自动调用以下函数：

print_paths

find_current_source_file

find_current_header_dir

find_current_library_file

find_cmakelists_current_dir

示例：

cmake
复制
编辑
list_template(PROJECT_ENABLE)
module_template([flag])
适用于模块化项目结构。自动调用以下函数：

print_paths

find_recurse_source_file

find_recurse_header_dir

find_recurse_library_file

📤 信息打印函数
print_all_code_sources([var_name])
打印并返回所有源文件。

print_all_code_includes([var_name])
打印并返回所有头文件路径。

print_all_code_librarys([var_name])
打印并返回所有静态库路径。

📝 全局变量说明
变量名	描述
ALL_CODE_SOURCES	所有收集到的源文件（.c/.cpp/.S）
ALL_CODE_INCLUDES	所有头文件包含路径
ALL_CODE_LIBRARIES	所有 .a 静态库文件路径