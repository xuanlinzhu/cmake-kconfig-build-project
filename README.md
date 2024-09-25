# cmake-kconfig-build-project

#### 介绍
创建了一个Kconfig配置参数，cmake构建工程且互相配合的中大型项目通用模板。

#### 软件架构
提供了用于cmake和Kconfig协同配置的工程模板
利用kconfig生成的配置关键字，用于控制camke的编译过程
同时关键字产生对应的宏定义，用于对应的代码实现

# 使用方式

    
## Cmake配置使用分为两种：
递归目录：` list_template()`
模块目录：` module_template()`
两个函数的参数都是依赖对应的宏，如果该宏存在，则该部分的cmake执行，可以不输入参数，一定会执行


## windows下：
进入到`cd .\project\template1\`路径下 

windows配置:`.\ck_script.bat cn`或者`.\ck_script.bat config`

windows构建:`.\ck_script.bat b`或者`.\ck_script.bat build`

windows编译:`.\ck_script.bat m`或者`.\ck_script.bat make`

windows清除:`.\ck_script.bat cl`或者`.\ck_script.bat clean`

windows自动配置、构建、编译:`.\ck_script.bat a`或者`.\ck_script.bat auto`

## Linux下：
进入到`cd .\project\template1\`路径下

Linux配置:`.\ck_script.sh cn`或者`.\ck_script.sh config`

Linux构建:`.\ck_script.sh b`或者`.\ck_script.sh build`

Linux编译:`.\ck_script.sh m`或者`.\ck_script.sh make`

Linux清除:`.\ck_script.sh cl`或者`.\ck_script.sh clean`

Linux自动配置、构建、编译:`.\ck_script.sh a`或者`.\ck_script.sh auto`
# CMake API 文档

## 概述

这个文档提供了关于 CMake 文件中定义的函数和宏的 API 信息。

## 函数

### `print_paths()`

这个函数用于输出当前源路径和当前构建路径。

### `list_template([temp_arg])`

非模块的构建模板函数。参数为相关的Kconfig配置的宏定义依赖。

例如`list_template(MOD1_ENABLE)`表示如果定义了`MOD1_ENABLE`该路径中的的所有源文件、汇编文件、头文件、静态库都会参与构建，同时会自动搜索下一级目录的CMakeLists.txt加入构建过程；没有定义则不会参与构建。

### `module_template([temp_arg])`

模块的构建模板函数。参数为相关的Kconfig配置的宏定义依赖。

例如`module_template(MOD1_ENABLE)`表示如果定义了`MOD1_ENABLE`该路径下（会递归搜索）的所有源文件、汇编文件、头文件、静态库都会参与构建；没有定义则不会参与构建。

### `find_current_source_file([output_variable])`

在当前目录查找源文件，并将结果输出在 `output_variable` 变量中。

### `find_recurse_source_file([output_variable])`

在当前目录及其子目录递归查找源文件，并将结果输出在 `output_variable` 变量中。

### `add_some_source_file(file1 [file2 ...])`

从全局变量中移除特定源文件

### `remove_some_source_file([output_variable])`

向项目中添加特定的源文件。

### `find_current_asm_file([output_variable])`

在当前目录查找汇编文件，并将结果输出在 `output_variable` 变量中。

### `find_recurse_asm_file([output_variable])`

在当前目录及其子目录递归查找汇编文件，并将结果输出在 `output_variable` 变量中。

### `add_some_asm_file(file1 [file2 ...])`

向项目中添加特定的汇编文件。

### `find_current_header_dir([output_variable])`

在当前目录查找头文件，并将结果输出在 `output_variable` 变量中。

### `find_recurse_header_dir([output_variable])`

在当前目录及其子目录递归查找头文件，并将结果输出在 `output_variable` 变量中。

### `add_some_header_dir(dir1 [dir2 ...])`

向项目中添加特定的头文件路径。

### `find_current_library_file([output_variable])`

在当前目录查找静态库，并将结果输出在 `output_variable` 变量中。

### `find_recurse_library_file([output_variable])`

在当前目录及其子目录递归查找静态库，并将结果输出在 `output_variable` 变量中。

### `add_some_library_file(file1 [file2 ...])`

向项目中添加特定的静态库文件。

### `set_external_path(PATH BINARY_NAME)`

添加外部路径，并指定与之对应的二进制目录。

### `find_cmakelists_current_dir([exclude_folders])`

查找当前目录下一级的所有构建文件，并添加到构建路径中。


