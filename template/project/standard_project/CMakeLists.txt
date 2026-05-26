# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-5-26
# Version: 2.1.0

# ==================================================
# CMake 基础配置
# ==================================================
# 选择较主流的现代 CMake 版本，便于使用 target_* 系列命令。
cmake_minimum_required(VERSION 3.20)

# 读取 Kconfig 生成的工程配置。
include(ck_config.cmake)

# 读取 CK CMake 公共函数库。
include(${CK_TOOLS_ROOT}/ck_tools/ck_cmlib.cmake)

# 读取工具链配置。
# 注意：这里需要在 project() 之前执行，确保编译器配置尽早生效。
include(${CK_TOOLS_ROOT}/ck_tools/ck_toolchain.cmake)

# 声明工程名称和语言类型。
# CXX 用于支持 C/C++ 混编，ASM 用于支持启动文件或汇编文件。
project(${PRO_NAME} LANGUAGES C CXX ASM)

message(STATUS "========== Start project configuration: ${PRO_NAME} ==========")
print_paths()

# ==================================================
# 输出目录配置
# ==================================================
# 将最终生成物统一输出到工程级 bin 目录。
set(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")

# 可执行文件输出目录，例如 .elf / .exe。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${OUTPUT_DIR}")

# 动态库输出目录，例如 .dll / .so / .dylib。
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${OUTPUT_DIR}")

# 静态库输出目录，例如 .a / .lib。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${OUTPUT_DIR}")

message(STATUS "Build output directory: ${OUTPUT_DIR}")

# ==================================================
# 用户配置区，可根据具体工程修改
# ==================================================
# 搜索当前工程目录下的源文件。
find_current_source_file()

# 搜索当前工程目录下的头文件路径。
find_current_header_dir()

# 配置外部 package 搜索路径。
set_external_path("${CK_WORKSPACE_ROOT}/package" "package")

# ==================================================
# 标准搜索区，一般不需要修改
# ==================================================
# 排除构建产物目录，避免递归扫描 build / bin。
find_cmakelists_current_dir("build" "bin")

# 收集并打印所有源文件、头文件路径和库文件。
print_all_code_sources(SRC_FILES)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

# ==================================================
# 工具链库搜索路径处理
# ==================================================
# TC_LIBRARY_DIRS 通常来自工具链配置，格式为以空格分隔的路径字符串。
# 这里统一转换为 CMake 列表，并解析为绝对路径。
set(_resolved_lib_dirs "")

if(DEFINED TC_LIBRARY_DIRS AND NOT "${TC_LIBRARY_DIRS}" STREQUAL "")
    string(REPLACE " " ";" TC_LIBRARY_DIRS_LIST "${TC_LIBRARY_DIRS}")

    foreach(dir ${TC_LIBRARY_DIRS_LIST})
        get_filename_component(abs_dir "${dir}" REALPATH BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
        list(APPEND _resolved_lib_dirs "${abs_dir}")
    endforeach()

    message(STATUS "Added library search paths: ${_resolved_lib_dirs}")
endif()

# ==================================================
# 目标文件定义
# ==================================================
# 创建最终可执行目标。
add_executable(${PRO_NAME} ${SRC_FILES})

# 添加头文件搜索路径。
# 使用 target_include_directories() 绑定到当前目标，避免污染全局作用域。
if(DEFINED INCLUDE_PATH AND NOT "${INCLUDE_PATH}" STREQUAL "")
    target_include_directories(${PRO_NAME} PRIVATE ${INCLUDE_PATH})
endif()

# 添加库搜索路径。
# 使用 target_link_directories() 替代全局 link_directories()，作用域更清晰。
if(_resolved_lib_dirs)
    target_link_directories(${PRO_NAME} PRIVATE ${_resolved_lib_dirs})
endif()

# ==================================================
# 编译宏定义
# ==================================================
# TC_DEFINE_MACROS 通常来自工具链配置，格式为以空格分隔的宏定义字符串。
if(DEFINED TC_DEFINE_MACROS AND NOT "${TC_DEFINE_MACROS}" STREQUAL "")
    string(REPLACE " " ";" TC_DEFINE_MACROS_LIST "${TC_DEFINE_MACROS}")

    target_compile_definitions(${PRO_NAME} PUBLIC ${TC_DEFINE_MACROS_LIST})
    message(STATUS "Added compile definitions: ${TC_DEFINE_MACROS}")
endif()

# ==================================================
# 链接库和链接选项
# ==================================================
# 添加工具链配置中的链接库。
if(DEFINED TC_LINK_LIBRARIES AND NOT "${TC_LINK_LIBRARIES}" STREQUAL "")
    string(REPLACE " " ";" TC_LINK_LIBRARIES_LIST "${TC_LINK_LIBRARIES}")

    target_link_libraries(${PRO_NAME} PRIVATE ${TC_LINK_LIBRARIES_LIST})
    message(STATUS "Added toolchain link libraries: ${TC_LINK_LIBRARIES}")
endif()

# 添加工程扫描到的库文件。
if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    target_link_libraries(${PRO_NAME} PRIVATE ${LIB_FILES})
    message(STATUS "Added project library files: ${LIB_FILES}")
endif()

# 生成 map 文件。
# 这里使用 target_link_options()，需要 CMake 3.13+，当前最低版本 3.20 已支持。
if(DEFINED TC_GENERATE_MAP_FILE AND TC_GENERATE_MAP_FILE)
    message(STATUS "Map file will be generated at: ${OUTPUT_DIR}/${PRO_NAME}.map")

    target_link_options(${PRO_NAME} PRIVATE
        "-Wl,-Map=${OUTPUT_DIR}/${PRO_NAME}.map"
        "-Wl,-cref"
    )
endif()

# ==================================================
# 构建后产物生成
# ==================================================
# 生成裸 bin 文件。
if(DEFINED TC_GENERATE_BIN AND TC_GENERATE_BIN)
    add_custom_command(TARGET ${PRO_NAME} POST_BUILD
        COMMAND ${TC_C_CXX_COMPILER}-objcopy -O binary $<TARGET_FILE:${PRO_NAME}> "${OUTPUT_DIR}/${PRO_NAME}.bin"
        COMMENT "Generating binary file: ${PRO_NAME}.bin"
        VERBATIM
    )
endif()

# 生成反汇编文件。
if(DEFINED TC_GENERATE_DISASSEMBLY AND TC_GENERATE_DISASSEMBLY)
    if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
        add_custom_command(TARGET ${PRO_NAME} POST_BUILD
            COMMAND cmd /c "${TC_C_CXX_COMPILER}-objdump -D $<TARGET_FILE:${PRO_NAME}> > ${OUTPUT_DIR}\\${PRO_NAME}.dis"
            COMMENT "Generating disassembly file on Windows: ${PRO_NAME}.dis"
            VERBATIM
        )
    else()
        add_custom_command(TARGET ${PRO_NAME} POST_BUILD
            COMMAND /bin/sh -c "${TC_C_CXX_COMPILER}-objdump -D $<TARGET_FILE:${PRO_NAME}> > ${OUTPUT_DIR}/${PRO_NAME}.dis"
            COMMENT "Generating disassembly file on Unix-like host: ${PRO_NAME}.dis"
            VERBATIM
        )
    endif()
endif()

# ==================================================
# 单元测试配置
# ==================================================
# 开启后会把当前目标注册为一个 CTest 测试项。
if(DEFINED CK_TEST_UNIT AND CK_TEST_UNIT)
    enable_testing()
    add_test(NAME ${PRO_NAME}_unit COMMAND $<TARGET_FILE:${PRO_NAME}>)
    message(STATUS "Registered unit test: ${PRO_NAME}_unit")
endif()
