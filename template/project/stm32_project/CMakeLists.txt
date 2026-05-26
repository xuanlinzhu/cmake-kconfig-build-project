# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2025-6-28
# Version: 2.0.0

# --------------------------------------------------
# CMake 基础配置
# --------------------------------------------------
# 设置 CMake 最低版本要求
cmake_minimum_required(VERSION 3.20)

# 引入 Kconfig 生成的配置
include(ck_config.cmake)

# 引入 CK CMake 工具库
include(${CK_TOOLS_ROOT}/ck_tools/ck_utils.cmake)

# STM32 工程通常由外部 toolchain 文件指定工具链
# 示例：
# cmake -S . -B build -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/gcc-arm-none-eabi.cmake
# include(${CK_TOOLS_ROOT}/ck_tools/ck_toolchain.cmake)

# 定义工程
project(${PRO_NAME} LANGUAGES C CXX ASM)

message(STATUS "========== Start project configuration: ${PRO_NAME} ==========")
print_paths()

# --------------------------------------------------
# 输出目录配置
# --------------------------------------------------
# 设置统一输出目录
set(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")

# 设置可执行文件输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})

# 设置共享库输出目录
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR})

# 设置静态库输出目录
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR})

message(STATUS "Build output directory: ${OUTPUT_DIR}")

# --------------------------------------------------
# 主目标定义
# --------------------------------------------------
# STM32 工程先创建空目标，后续再追加源码、头文件和库
add_executable(${PRO_NAME})

# 固定输出文件后缀为 .elf
set_target_properties(${PRO_NAME} PROPERTIES
    SUFFIX ".elf"
)

# --------------------------------------------------
# CubeMX 生成部分
# --------------------------------------------------
# 添加 CubeMX 生成的 CMake 子工程
add_subdirectory(cmake/stm32cubemx)

# --------------------------------------------------
# 用户配置区，可修改
# --------------------------------------------------
# 搜索当前工程头文件目录
find_current_header_dir()

# 添加外部模块路径
set_external_path("${CK_WORKSPACE_ROOT}/package" "package")

# --------------------------------------------------
# 标准搜索区，一般不修改
# --------------------------------------------------
# 搜索当前目录下一级 CMake 模块
# STM32 工程需要排除 CubeMX 相关目录，避免重复添加源码
find_cmakelists_current_dir(
    "build"
    "bin"
    "cmake"
    "Core"
    "Drivers"
)

# 打印并导出源码、头文件路径和库文件
print_all_code_sources(SRC_FILES)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

# --------------------------------------------------
# 目标源码配置
# --------------------------------------------------
# 将收集到的源码加入主目标
if(DEFINED SRC_FILES AND NOT "${SRC_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES SRC_FILES)

    target_sources(${PRO_NAME}
        PRIVATE
            ${SRC_FILES}
    )
endif()

# --------------------------------------------------
# 目标头文件路径配置
# --------------------------------------------------
# 将收集到的头文件路径加入主目标
if(DEFINED INCLUDE_PATH AND NOT "${INCLUDE_PATH}" STREQUAL "")
    list(REMOVE_DUPLICATES INCLUDE_PATH)

    target_include_directories(${PRO_NAME}
        PRIVATE
            ${INCLUDE_PATH}
    )
endif()

# --------------------------------------------------
# 链接库路径配置
# --------------------------------------------------
# 添加工具链或 Kconfig 配置中的库搜索路径
if(DEFINED TC_LIBRARY_DIRS AND NOT TC_LIBRARY_DIRS STREQUAL "")
    string(REPLACE " " ";" TC_LIBRARY_DIRS_LIST "${TC_LIBRARY_DIRS}")

    set(_resolved_lib_dirs "")
    foreach(dir ${TC_LIBRARY_DIRS_LIST})
        get_filename_component(abs_dir "${dir}" REALPATH BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
        list(APPEND _resolved_lib_dirs "${abs_dir}")
    endforeach()

    if(_resolved_lib_dirs)
        target_link_directories(${PRO_NAME}
            PRIVATE
                ${_resolved_lib_dirs}
        )

        message(STATUS "Added library paths: ${_resolved_lib_dirs}")
    endif()
endif()

# --------------------------------------------------
# 编译宏配置
# --------------------------------------------------
# 添加工具链或 Kconfig 配置中的预定义宏
if(DEFINED TC_DEFINE_MACROS AND NOT TC_DEFINE_MACROS STREQUAL "")
    string(REPLACE " " ";" TC_DEFINE_MACROS_LIST "${TC_DEFINE_MACROS}")

    target_compile_definitions(${PRO_NAME}
        PUBLIC
            ${TC_DEFINE_MACROS_LIST}
    )

    message(STATUS "Added macro definitions: ${TC_DEFINE_MACROS_LIST}")
endif()

# --------------------------------------------------
# STM32 链接修正
# --------------------------------------------------
# 清理部分 Windows/MinGW 环境下可能出现的错误隐式库
list(REMOVE_ITEM CMAKE_C_IMPLICIT_LINK_LIBRARIES ob)

# --------------------------------------------------
# 链接库配置
# --------------------------------------------------
# 注意：
# cmake/stm32cubemx/CMakeLists.txt 对 ${PRO_NAME} 使用了 plain signature：
# target_link_libraries(${PRO_NAME} ...)
# 所以这里也必须保持 plain signature，不能写 PRIVATE/PUBLIC/INTERFACE。
target_link_libraries(${PRO_NAME}
    stm32cubemx
)

# 添加工具链或 Kconfig 配置中的链接库
if(DEFINED TC_LINK_LIBRARIES AND NOT TC_LINK_LIBRARIES STREQUAL "")
    string(REPLACE " " ";" TC_LINK_LIBRARIES_LIST "${TC_LINK_LIBRARIES}")

    target_link_libraries(${PRO_NAME}
        ${TC_LINK_LIBRARIES_LIST}
    )

    message(STATUS "Added link libraries: ${TC_LINK_LIBRARIES_LIST}")
endif()

# 添加扫描到的库文件
if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES LIB_FILES)

    target_link_libraries(${PRO_NAME}
        ${LIB_FILES}
    )
endif()

# --------------------------------------------------
# Map 文件配置
# --------------------------------------------------
# STM32 工程默认生成 map 文件
if(NOT DEFINED TC_GENERATE_MAP_FILE)
    set(TC_GENERATE_MAP_FILE ON)
endif()

if(TC_GENERATE_MAP_FILE)
    set(MAP_FILE "${OUTPUT_DIR}/${PRO_NAME}.map")

    message(STATUS "Map file will be generated at: ${MAP_FILE}")

    target_link_options(${PRO_NAME}
        PRIVATE
            "-Wl,-Map=${MAP_FILE}"
            "-Wl,--cref"
            "-Wl,--print-memory-usage"
    )
endif()

# --------------------------------------------------
# 工具查找
# --------------------------------------------------
# 优先使用工具链文件提供的工具路径，否则自动查找
if(NOT CMAKE_OBJCOPY)
    find_program(CMAKE_OBJCOPY arm-none-eabi-objcopy)
endif()

if(NOT CMAKE_OBJDUMP)
    find_program(CMAKE_OBJDUMP arm-none-eabi-objdump)
endif()

if(NOT CMAKE_SIZE)
    find_program(CMAKE_SIZE arm-none-eabi-size)
endif()

message(STATUS "CMAKE_OBJCOPY = ${CMAKE_OBJCOPY}")
message(STATUS "CMAKE_OBJDUMP = ${CMAKE_OBJDUMP}")
message(STATUS "CMAKE_SIZE    = ${CMAKE_SIZE}")

# --------------------------------------------------
# 构建产物路径
# --------------------------------------------------
set(ELF_FILE  $<TARGET_FILE:${PRO_NAME}>)
set(BIN_FILE  "${OUTPUT_DIR}/${PRO_NAME}.bin")
set(DIS_FILE  "${OUTPUT_DIR}/${PRO_NAME}.dis")
set(SIZE_FILE "${OUTPUT_DIR}/${PRO_NAME}.size.txt")

# --------------------------------------------------
# Bin 文件生成
# --------------------------------------------------
# STM32 工程默认生成 bin 文件
if(NOT DEFINED TC_GENERATE_BIN)
    set(TC_GENERATE_BIN ON)
endif()

if(TC_GENERATE_BIN AND CMAKE_OBJCOPY)
    add_custom_command(
        OUTPUT ${BIN_FILE}
        COMMAND ${CMAKE_COMMAND} -E make_directory ${OUTPUT_DIR}
        COMMAND ${CMAKE_OBJCOPY} -O binary ${ELF_FILE} ${BIN_FILE}
        DEPENDS ${PRO_NAME}
        COMMENT "Generating binary file: ${PRO_NAME}.bin"
        VERBATIM
    )

    add_custom_target(${PRO_NAME}_bin ALL
        DEPENDS ${BIN_FILE}
    )
endif()

# --------------------------------------------------
# Disassembly 文件生成
# --------------------------------------------------
# STM32 工程默认生成反汇编文件
if(NOT DEFINED TC_GENERATE_DISASSEMBLY)
    set(TC_GENERATE_DISASSEMBLY ON)
endif()

if(TC_GENERATE_DISASSEMBLY AND CMAKE_OBJDUMP)
    set(OBJDUMP_SCRIPT "${CMAKE_BINARY_DIR}/objdump_to_file.cmake")

    file(WRITE ${OBJDUMP_SCRIPT}
"execute_process(
    COMMAND \"${CMAKE_OBJDUMP}\" -D \"${OUTPUT_DIR}/${PRO_NAME}.elf\"
    OUTPUT_FILE \"${DIS_FILE}\"
    RESULT_VARIABLE _objdump_result
)
if(NOT _objdump_result EQUAL 0)
    message(FATAL_ERROR \"objdump failed: \${_objdump_result}\")
endif()
")

    add_custom_command(
        OUTPUT ${DIS_FILE}
        COMMAND ${CMAKE_COMMAND} -P ${OBJDUMP_SCRIPT}
        DEPENDS ${PRO_NAME}
        COMMENT "Generating disassembly file: ${PRO_NAME}.dis"
        VERBATIM
    )

    add_custom_target(${PRO_NAME}_dis ALL
        DEPENDS ${DIS_FILE}
    )
endif()

# --------------------------------------------------
# Size 信息生成
# --------------------------------------------------
# STM32 工程默认打印并保存 ELF 段大小
if(NOT DEFINED TC_PRINT_SIZE)
    set(TC_PRINT_SIZE ON)
endif()

if(TC_PRINT_SIZE AND CMAKE_SIZE)
    set(SIZE_SCRIPT "${CMAKE_BINARY_DIR}/size_to_file.cmake")

    file(WRITE ${SIZE_SCRIPT}
"execute_process(
    COMMAND \"${CMAKE_SIZE}\" --format=berkeley \"${OUTPUT_DIR}/${PRO_NAME}.elf\"
    RESULT_VARIABLE _size_print_result
)
if(NOT _size_print_result EQUAL 0)
    message(FATAL_ERROR \"size print failed: \${_size_print_result}\")
endif()

execute_process(
    COMMAND \"${CMAKE_SIZE}\" -A \"${OUTPUT_DIR}/${PRO_NAME}.elf\"
    OUTPUT_FILE \"${SIZE_FILE}\"
    RESULT_VARIABLE _size_save_result
)
if(NOT _size_save_result EQUAL 0)
    message(FATAL_ERROR \"size save failed: \${_size_save_result}\")
endif()
")

    add_custom_command(
        OUTPUT ${SIZE_FILE}
        COMMAND ${CMAKE_COMMAND} -P ${SIZE_SCRIPT}
        DEPENDS ${PRO_NAME}
        COMMENT "Printing and saving ELF section sizes"
        VERBATIM
    )

    add_custom_target(${PRO_NAME}_size ALL
        DEPENDS ${SIZE_FILE}
    )
endif()

# --------------------------------------------------
# 单元测试配置
# --------------------------------------------------
# 如果启用 CK_TEST_UNIT，则注册当前目标为测试程序
if(DEFINED CK_TEST_UNIT AND CK_TEST_UNIT)
    enable_testing()

    add_test(
        NAME ${PRO_NAME}_unit
        COMMAND $<TARGET_FILE:${PRO_NAME}>
    )
endif()

message(STATUS "========== Project configuration finished: ${PRO_NAME} ==========")
