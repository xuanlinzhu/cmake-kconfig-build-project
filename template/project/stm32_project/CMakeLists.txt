# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-5-26
# Version: 2.4.0

# --------------------------------------------------
# CMake 基础配置
# --------------------------------------------------
# 设置 CMake 最低版本要求。
cmake_minimum_required(VERSION 3.20)

# 引入 Kconfig 生成的配置。
include(ck_config.cmake)

# 引入 CK CMake 工具库。
include(${CK_TOOLS_ROOT}/ck_tools/ck_utils.cmake)

# 引入 CK 工程通用函数库。
include(${CK_TOOLS_ROOT}/ck_tools/ck_project.cmake)

# STM32 工程通常由外部 toolchain 文件指定工具链。

# 定义工程。
project(${PRO_NAME} LANGUAGES C CXX ASM)

ck_project_begin(${PRO_NAME})

# --------------------------------------------------
# 工程默认配置
# --------------------------------------------------
# STM32 工程默认输出 .elf，并默认生成 map / bin / dis / size。
ck_profile_stm32()
ck_project_set_defaults()

# --------------------------------------------------
# 输出目录配置
# --------------------------------------------------
# 设置统一输出目录。
ck_set_output_dirs(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")

# --------------------------------------------------
# 主目标定义
# --------------------------------------------------
# STM32 工程先创建空目标，后续再追加源码、头文件和库。
ck_create_target(${PRO_NAME})

# --------------------------------------------------
# 平台扩展区，可根据具体工程修改
# --------------------------------------------------
# 添加 CubeMX 生成的 CMake 子工程。
# 注意：CubeMX 子工程负责添加 Core / Drivers 等 STM32 底层源码。
add_subdirectory(cmake/stm32cubemx)

# --------------------------------------------------
# 用户配置区，可修改
# --------------------------------------------------
# 如果某个工程需要排除额外目录，可以在扫描前追加：
# list(APPEND CK_EXCLUDE_DIRS "third_party" "generated")

# 如果某个工程需要手动追加源码、头文件或库文件，可以在这里追加：
# list(APPEND SRC_FILES "user_file.c")
# list(APPEND INCLUDE_PATH "user_include")
# list(APPEND LIB_FILES "user_lib.a")

# --------------------------------------------------
# 工程扫描区，一般不修改
# --------------------------------------------------
# STM32 工程的 Core / Drivers 源码由 CubeMX 子工程添加，当前模板只扫描工程头文件路径。
# 如果用户源码不在子 CMake 模块中，可以取消下一行注释：
# ck_collect_current_sources()
ck_collect_current_includes()

# 从 Kconfig 的外部模块配置入口自动添加构建搜索路径。
ck_collect_kconfig_external_paths(KCONFIG_FILE "${CMAKE_CURRENT_SOURCE_DIR}/Kconfig")

# 搜索当前目录下一层 CMake 模块。
ck_collect_cmake_subdirs()

# 收集并打印所有源文件、头文件路径和库文件。
ck_collect_print_project_files()

# 避免递归扫描、外部模块和子 CMake 重复添加同一个文件或路径。
ck_normalize_project_files()

# --------------------------------------------------
# 目标源码和头文件配置
# --------------------------------------------------
# 将工程扫描到的源码和头文件路径加入主目标。
ck_target_apply_sources(${PRO_NAME})
ck_target_apply_includes(${PRO_NAME})

# --------------------------------------------------
# 工具链编译配置
# --------------------------------------------------
# 添加工具链或 Kconfig 配置中的库搜索路径和宏定义。
ck_target_apply_library_dirs(${PRO_NAME})
ck_target_apply_definitions(${PRO_NAME})

# --------------------------------------------------
# 平台链接修正
# --------------------------------------------------
# 清理部分 Windows / MinGW 环境下可能出现的错误隐式库。
list(REMOVE_ITEM CMAKE_C_IMPLICIT_LINK_LIBRARIES ob)

# --------------------------------------------------
# 链接库配置
# --------------------------------------------------
# 注意：
# cmake/stm32cubemx/CMakeLists.txt 对 ${PRO_NAME} 通常使用 plain signature。
# ck_profile_stm32() 已经将 CK_LINK_LIBRARIES_MODE 设置为 plain。
ck_target_link_libraries(${PRO_NAME}
    stm32cubemx
)

# 添加工具链或 Kconfig 配置中的链接库。
ck_target_apply_toolchain_libraries(${PRO_NAME})

# 添加工程扫描到的库文件。
ck_target_apply_project_libraries(${PRO_NAME})

# --------------------------------------------------
# Map 文件配置
# --------------------------------------------------
# STM32 工程默认生成 map 文件，并打印内存使用情况。
ck_target_enable_map(${PRO_NAME})
# --print-map-locals 用于输出本地符号，-u,_printf_float 用于启用 printf 浮点格式支持。
target_link_options(${CMAKE_PROJECT_NAME}
    PRIVATE
        "-Wl,--print-map-locals"
        "-Wl,-u,_printf_float"
)
# --------------------------------------------------
# 工具查找
# --------------------------------------------------
# 优先使用工具链文件提供的工具路径，否则按当前编译器前缀和 ARM GCC 名称查找。
ck_find_binutils_tool(CMAKE_OBJCOPY
    TOOL_NAME objcopy
    NAMES arm-none-eabi-objcopy
    FALLBACK_NAME "bin"
)

ck_find_binutils_tool(CMAKE_OBJDUMP
    TOOL_NAME objdump
    NAMES arm-none-eabi-objdump
    FALLBACK_NAME "disassembly"
)

ck_find_binutils_tool(CMAKE_SIZE
    TOOL_NAME size
    NAMES arm-none-eabi-size
    FALLBACK_NAME "size"
)

ck_print_binutils_tools()

# --------------------------------------------------
# 构建产物生成
# --------------------------------------------------
# STM32 工程默认生成 bin、反汇编文件，并打印 / 保存 size 信息。
ck_target_generate_bin(${PRO_NAME})
ck_target_generate_disassembly(${PRO_NAME})
ck_target_generate_size(${PRO_NAME})

# --------------------------------------------------
# 单元测试配置
# --------------------------------------------------
# 如果启用 CK_TEST_UNIT，则注册当前目标为测试程序。
ck_target_enable_test(${PRO_NAME})

ck_project_end(${PRO_NAME})
