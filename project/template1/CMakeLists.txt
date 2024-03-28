# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2024-3-26
# Version: 1.0
#
# Description: 这个文件用于CMakeLists的顶层文件
# cmake最低版本要求
cmake_minimum_required(VERSION 3.5)

include(ck_cmlib.cmake)

set(PRO_NAME "ck_template" )
project(${PRO_NAME})

# 启用汇编语言
enable_language(ASM)

message("---------------开始构建----------------")
print_paths()

set(OUTPUT_DIR "bin")
# 控制生成的可执行文件（例如：.exe 文件）的输出目录。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../../../)
#控制生成的共享库（例如：.dll 文件）的输出目录
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../../../)
#控制生成的静态库（例如：.lib 文件）的输出目录。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../../../)
#设置工程名字

# 设置C语言版本
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 寻找当前文件夹的源文件
find_current_source_file()
find_current_header_dir()

# 配置外部工程路径
set_external_path("${CMAKE_CURRENT_SOURCE_DIR}/../../source" "ex_source")
# 排除搜索路径
find_cmakelists_current_dir("build")

print_all_code_sources(SRC_FILES)
print_all_asm_sources(ASM_FILES)
# 把对应的文件标记为汇编文件
set_source_files_properties(${ASM_FILES} PROPERTIES LANGUAGE ASM)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

INCLUDE_DIRECTORIES(${INCLUDE_PATH})

add_executable(${PRO_NAME} ${SRC_FILES} ${ASM_FILES})

# target_link_libraries(${LIB_FILES})
