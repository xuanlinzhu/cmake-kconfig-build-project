# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-5-26
# Version: 2.4.0

# ==================================================
# CMake 基础配置
# ==================================================
# 选择较主流的现代 CMake 版本，便于使用 target_* 系列命令。
cmake_minimum_required(VERSION 3.20)

# 读取 Kconfig 生成的工程配置。
include(ck_config.cmake)

# 读取 CK CMake 公共函数库。
include(${CK_TOOLS_ROOT}/ck_tools/ck_utils.cmake)

# 读取工具链配置。
# 注意：这里需要在 project() 之前执行，确保编译器配置尽早生效。
include(${CK_TOOLS_ROOT}/ck_tools/ck_toolchain.cmake)

# 读取 CK 工程通用函数库。
include(${CK_TOOLS_ROOT}/ck_tools/ck_project.cmake)

# 声明工程名称和语言类型。
# CXX 用于支持 C/C++ 混编，ASM 用于支持启动文件或汇编文件。
project(${PRO_NAME} LANGUAGES C CXX ASM)

ck_project_begin(${PRO_NAME})

# ==================================================
# 工程默认配置
# ==================================================
# 通用工程默认不强制设置目标后缀，不默认生成 bin / dis / size。
ck_profile_generic()
ck_project_set_defaults()

# ==================================================
# 输出目录配置
# ==================================================
# 将最终生成物统一输出到工程级 bin 目录。
ck_set_output_dirs(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")

# ==================================================
# 主目标定义
# ==================================================
# 先创建空目标，后续通过 target_sources() 统一追加源码。
ck_create_target(${PRO_NAME})

# ==================================================
# 平台扩展区，可根据具体工程修改
# ==================================================
# 如果 STM32 / ZYNQ / Linux 等工程需要添加专用子工程，可以在对应模板中添加：
# add_subdirectory(cmake/vendor_sdk)
# ck_target_link_libraries(${PRO_NAME} vendor_sdk)

# ==================================================
# 用户配置区，可根据具体工程修改
# ==================================================
# 如果某个工程需要排除额外目录，可以在扫描前追加：
# list(APPEND CK_EXCLUDE_DIRS "third_party" "generated")

# 如果某个工程需要手动追加源码、头文件或库文件，可以在这里追加：
# list(APPEND SRC_FILES "user_file.c")
# list(APPEND INCLUDE_PATH "user_include")
# list(APPEND LIB_FILES "user_lib.a")

# ==================================================
# 工程扫描区，一般不需要修改
# ==================================================
# 搜索当前工程目录下的源文件和头文件路径。
ck_collect_current_sources()
ck_collect_current_includes()

# 从 Kconfig 的外部模块配置入口自动添加构建搜索路径。
ck_collect_kconfig_external_paths(KCONFIG_FILE "${CMAKE_CURRENT_SOURCE_DIR}/Kconfig")

# 搜索当前目录下一层 CMake 模块。
ck_collect_cmake_subdirs()

# 收集并打印所有源文件、头文件路径和库文件。
ck_collect_print_project_files()

# 避免递归扫描、外部模块和子 CMake 重复添加同一个文件或路径。
ck_normalize_project_files()

# ==================================================
# 目标源码和头文件配置
# ==================================================
# 将工程扫描到的源码和头文件路径加入主目标。
ck_target_apply_sources(${PRO_NAME})
ck_target_apply_includes(${PRO_NAME})

# ==================================================
# 工具链编译配置
# ==================================================
# 添加工具链或 Kconfig 配置中的库搜索路径和宏定义。
ck_target_apply_library_dirs(${PRO_NAME})
ck_target_apply_definitions(${PRO_NAME})

# ==================================================
# 平台链接修正
# ==================================================
# 通用模板默认不做平台链接修正。

# ==================================================
# 链接库配置
# ==================================================
# 添加工具链或 Kconfig 配置中的链接库。
ck_target_apply_toolchain_libraries(${PRO_NAME})

# 添加工程扫描到的库文件。
ck_target_apply_project_libraries(${PRO_NAME})

# ==================================================
# Map 文件配置
# ==================================================
# 如果 TC_GENERATE_MAP_FILE 开启，则生成 map 文件。
ck_target_enable_map(${PRO_NAME})

# ==================================================
# 工具查找
# ==================================================
# 优先使用工具链文件提供的工具路径，否则按当前编译器前缀查找。
ck_find_binutils_tool(CMAKE_OBJCOPY
    TOOL_NAME objcopy
)

ck_find_binutils_tool(CMAKE_OBJDUMP
    TOOL_NAME objdump
)

ck_find_binutils_tool(CMAKE_SIZE
    TOOL_NAME size
)

ck_print_binutils_tools()

# ==================================================
# 构建产物生成
# ==================================================
# 是否生成 bin / dis / size 由 TC_GENERATE_BIN / TC_GENERATE_DISASSEMBLY / TC_PRINT_SIZE 控制。
ck_target_generate_bin(${PRO_NAME})
ck_target_generate_disassembly(${PRO_NAME})
ck_target_generate_size(${PRO_NAME})

# ==================================================
# 单元测试配置
# ==================================================
# 如果启用 CK_TEST_UNIT，则注册当前目标为测试程序。
ck_target_enable_test(${PRO_NAME})

ck_project_end(${PRO_NAME})
