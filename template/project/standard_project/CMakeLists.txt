# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-5-26
# Version: 2.2.0

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

# 声明工程名称和语言类型。
# CXX 用于支持 C/C++ 混编，ASM 用于支持启动文件或汇编文件。
project(${PRO_NAME} LANGUAGES C CXX ASM)

message(STATUS "========== Start project configuration: ${PRO_NAME} ==========")
print_paths()

# ==================================================
# 标准模板默认配置
# ==================================================
# 工程类型预留字段。
# 当前标准模板默认使用 generic，STM32 / ZYNQ 等工程可在独立扩展区中覆盖相关变量。
if(NOT DEFINED CK_PROJECT_TYPE)
    set(CK_PROJECT_TYPE "generic")
endif()

# target_link_libraries() 默认使用现代作用域签名。
# 如果某些外部子工程已经对同一个 target 使用 plain signature，可改为 plain。
if(NOT DEFINED CK_LINK_LIBRARIES_MODE)
    set(CK_LINK_LIBRARIES_MODE "scoped")
endif()

# 目标文件后缀默认不强制设置。
# 嵌入式工程可设置为 .elf，普通 PC 工程保持默认即可。
if(NOT DEFINED CK_TARGET_SUFFIX)
    set(CK_TARGET_SUFFIX "")
endif()

# 默认排除构建产物目录，避免递归扫描 build / bin。
# 具体工程可在用户配置区继续 list(APPEND CK_EXCLUDE_DIRS xxx)。
if(NOT DEFINED CK_EXCLUDE_DIRS)
    set(CK_EXCLUDE_DIRS
        build
        bin
    )
else()
    list(APPEND CK_EXCLUDE_DIRS
        build
        bin
    )
endif()

list(REMOVE_DUPLICATES CK_EXCLUDE_DIRS)

message(STATUS "Project type: ${CK_PROJECT_TYPE}")
message(STATUS "Link libraries mode: ${CK_LINK_LIBRARIES_MODE}")
message(STATUS "Excluded directories: ${CK_EXCLUDE_DIRS}")

# ==================================================
# 通用辅助函数
# ==================================================
# 统一封装 target_link_libraries()。
# 默认使用 PRIVATE；遇到外部 CMake 使用 plain signature 时，可以切换为 plain。
function(ck_target_link_libraries target)
    if("${ARGN}" STREQUAL "")
        return()
    endif()

    if(CK_LINK_LIBRARIES_MODE STREQUAL "plain")
        target_link_libraries(${target} ${ARGN})
    else()
        target_link_libraries(${target} PRIVATE ${ARGN})
    endif()
endfunction()

# 尝试查找 binutils 工具。
# 优先使用工具链文件显式提供的 CMAKE_xxx，其次从编译器同目录查找，最后从 PATH 查找。
function(ck_find_binutils_tool output_var)
    set(options)
    set(oneValueArgs FALLBACK_NAME)
    set(multiValueArgs NAMES)
    cmake_parse_arguments(CK_TOOL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(${output_var})
        return()
    endif()

    set(_tool_hints "")

    if(DEFINED CMAKE_C_COMPILER AND NOT "${CMAKE_C_COMPILER}" STREQUAL "")
        get_filename_component(_compiler_dir "${CMAKE_C_COMPILER}" DIRECTORY)
        if(_compiler_dir)
            list(APPEND _tool_hints "${_compiler_dir}")
        endif()
    endif()

    if(_tool_hints)
        find_program(${output_var}
            NAMES ${CK_TOOL_NAMES}
            HINTS ${_tool_hints}
            NO_DEFAULT_PATH
        )
    endif()

    if(NOT ${output_var})
        find_program(${output_var}
            NAMES ${CK_TOOL_NAMES}
        )
    endif()

    if(NOT ${output_var} AND CK_TOOL_FALLBACK_NAME)
        message(STATUS "${output_var} not found, ${CK_TOOL_FALLBACK_NAME} generation will be skipped if enabled")
    endif()
endfunction()

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
# 目标文件定义
# ==================================================
# 先创建空目标，后续通过 target_sources() 统一追加源码。
add_executable(${PRO_NAME})

# 如果工程需要固定后缀，例如嵌入式 .elf，可通过 CK_TARGET_SUFFIX 设置。
if(NOT "${CK_TARGET_SUFFIX}" STREQUAL "")
    set_target_properties(${PRO_NAME} PROPERTIES
        SUFFIX "${CK_TARGET_SUFFIX}"
    )
endif()

# ==================================================
# 用户配置区，可根据具体工程修改
# ==================================================
# 搜索当前工程目录下的源文件。
find_current_source_file()

# 搜索当前工程目录下的头文件路径。
find_current_header_dir()

# 从 Kconfig 的外部模块配置入口自动添加构建搜索路径。
ck_add_kconfig_external_paths("${CMAKE_CURRENT_SOURCE_DIR}/Kconfig")

# 如果某个工程需要排除额外目录，可以在这里追加：
# list(APPEND CK_EXCLUDE_DIRS "third_party" "generated")

# ==================================================
# 标准搜索区，一般不需要修改
# ==================================================
# 搜索当前目录下一层 CMake 模块。
find_cmakelists_current_dir(${CK_EXCLUDE_DIRS})

# 收集并打印所有源文件、头文件路径和库文件。
print_all_code_sources(SRC_FILES)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

# ==================================================
# 源码、头文件和库文件去重
# ==================================================
# 避免递归扫描、外部模块和子 CMake 重复添加同一个文件或路径。
if(DEFINED SRC_FILES AND NOT "${SRC_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES SRC_FILES)
endif()

if(DEFINED INCLUDE_PATH AND NOT "${INCLUDE_PATH}" STREQUAL "")
    list(REMOVE_DUPLICATES INCLUDE_PATH)
endif()

if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES LIB_FILES)
endif()

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

    list(REMOVE_DUPLICATES _resolved_lib_dirs)
    message(STATUS "Added library search paths: ${_resolved_lib_dirs}")
endif()

# ==================================================
# 目标源码配置
# ==================================================
# 将收集到的源码加入主目标。
if(DEFINED SRC_FILES AND NOT "${SRC_FILES}" STREQUAL "")
    target_sources(${PRO_NAME}
        PRIVATE
            ${SRC_FILES}
    )
endif()

# ==================================================
# 目标头文件路径配置
# ==================================================
# 使用 target_include_directories() 绑定到当前目标，避免污染全局作用域。
if(DEFINED INCLUDE_PATH AND NOT "${INCLUDE_PATH}" STREQUAL "")
    target_include_directories(${PRO_NAME}
        PRIVATE
            ${INCLUDE_PATH}
    )
endif()

# ==================================================
# 链接库路径配置
# ==================================================
# 使用 target_link_directories() 替代全局 link_directories()，作用域更清晰。
if(_resolved_lib_dirs)
    target_link_directories(${PRO_NAME}
        PRIVATE
            ${_resolved_lib_dirs}
    )
endif()

# ==================================================
# 编译宏定义
# ==================================================
# TC_DEFINE_MACROS 通常来自工具链配置，格式为以空格分隔的宏定义字符串。
if(DEFINED TC_DEFINE_MACROS AND NOT "${TC_DEFINE_MACROS}" STREQUAL "")
    string(REPLACE " " ";" TC_DEFINE_MACROS_LIST "${TC_DEFINE_MACROS}")

    target_compile_definitions(${PRO_NAME}
        PUBLIC
            ${TC_DEFINE_MACROS_LIST}
    )

    message(STATUS "Added compile definitions: ${TC_DEFINE_MACROS_LIST}")
endif()

# ==================================================
# 链接库配置
# ==================================================
# 添加工具链配置中的链接库。
if(DEFINED TC_LINK_LIBRARIES AND NOT "${TC_LINK_LIBRARIES}" STREQUAL "")
    string(REPLACE " " ";" TC_LINK_LIBRARIES_LIST "${TC_LINK_LIBRARIES}")

    ck_target_link_libraries(${PRO_NAME} ${TC_LINK_LIBRARIES_LIST})
    message(STATUS "Added toolchain link libraries: ${TC_LINK_LIBRARIES_LIST}")
endif()

# 添加工程扫描到的库文件。
if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    ck_target_link_libraries(${PRO_NAME} ${LIB_FILES})
    message(STATUS "Added project library files: ${LIB_FILES}")
endif()

# ==================================================
# Map 文件配置
# ==================================================
# 生成 map 文件。
# 这里使用 target_link_options()，需要 CMake 3.13+，当前最低版本 3.20 已支持。
if(DEFINED TC_GENERATE_MAP_FILE AND TC_GENERATE_MAP_FILE)
    set(MAP_FILE "${OUTPUT_DIR}/${PRO_NAME}.map")

    message(STATUS "Map file will be generated at: ${MAP_FILE}")

    target_link_options(${PRO_NAME}
        PRIVATE
            "-Wl,-Map=${MAP_FILE}"
            "-Wl,-cref"
    )
endif()

# ==================================================
# 工具查找
# ==================================================
# 优先使用工具链文件提供的 CMAKE_OBJCOPY / CMAKE_OBJDUMP / CMAKE_SIZE。
# 如果工具链文件未提供，则尝试从编译器目录或 PATH 中查找。
ck_find_binutils_tool(CMAKE_OBJCOPY
    NAMES objcopy arm-none-eabi-objcopy
    FALLBACK_NAME "bin"
)

ck_find_binutils_tool(CMAKE_OBJDUMP
    NAMES objdump arm-none-eabi-objdump
    FALLBACK_NAME "disassembly"
)

ck_find_binutils_tool(CMAKE_SIZE
    NAMES size arm-none-eabi-size
    FALLBACK_NAME "size"
)

message(STATUS "CMAKE_OBJCOPY = ${CMAKE_OBJCOPY}")
message(STATUS "CMAKE_OBJDUMP = ${CMAKE_OBJDUMP}")
message(STATUS "CMAKE_SIZE    = ${CMAKE_SIZE}")

# ==================================================
# 构建产物路径
# ==================================================
set(TARGET_FILE $<TARGET_FILE:${PRO_NAME}>)
set(BIN_FILE    "${OUTPUT_DIR}/${PRO_NAME}.bin")
set(DIS_FILE    "${OUTPUT_DIR}/${PRO_NAME}.dis")
set(SIZE_FILE   "${OUTPUT_DIR}/${PRO_NAME}.size.txt")

# ==================================================
# Bin 文件生成
# ==================================================
# 生成裸 bin 文件。
if(DEFINED TC_GENERATE_BIN AND TC_GENERATE_BIN)
    if(CMAKE_OBJCOPY)
        add_custom_command(
            OUTPUT ${BIN_FILE}
            COMMAND ${CMAKE_COMMAND} -E make_directory "${OUTPUT_DIR}"
            COMMAND ${CMAKE_OBJCOPY} -O binary ${TARGET_FILE} "${BIN_FILE}"
            DEPENDS ${PRO_NAME}
            COMMENT "Generating binary file: ${PRO_NAME}.bin"
            VERBATIM
        )

        add_custom_target(${PRO_NAME}_bin ALL
            DEPENDS ${BIN_FILE}
        )
    else()
        message(WARNING "TC_GENERATE_BIN is enabled, but CMAKE_OBJCOPY was not found")
    endif()
endif()

# ==================================================
# Disassembly 文件生成
# ==================================================
# 生成反汇编文件。
if(DEFINED TC_GENERATE_DISASSEMBLY AND TC_GENERATE_DISASSEMBLY)
    if(CMAKE_OBJDUMP)
        set(OBJDUMP_SCRIPT "${CMAKE_BINARY_DIR}/ck_objdump_to_file.cmake")

        file(WRITE "${OBJDUMP_SCRIPT}"
            "execute_process(
                COMMAND \"\${CK_OBJDUMP}\" -D \"\${CK_INPUT_FILE}\"
                OUTPUT_FILE \"\${CK_OUTPUT_FILE}\"
                RESULT_VARIABLE _objdump_result
            )
            if(NOT _objdump_result EQUAL 0)
                message(FATAL_ERROR \"objdump failed: \${_objdump_result}\")
            endif()
        ")

        add_custom_command(
            OUTPUT ${DIS_FILE}
            COMMAND ${CMAKE_COMMAND}
                "-DCK_OBJDUMP=${CMAKE_OBJDUMP}"
                "-DCK_INPUT_FILE=${TARGET_FILE}"
                "-DCK_OUTPUT_FILE=${DIS_FILE}"
                -P "${OBJDUMP_SCRIPT}"
            DEPENDS ${PRO_NAME}
            COMMENT "Generating disassembly file: ${PRO_NAME}.dis"
            VERBATIM
        )

        add_custom_target(${PRO_NAME}_dis ALL
            DEPENDS ${DIS_FILE}
        )
    else()
        message(WARNING "TC_GENERATE_DISASSEMBLY is enabled, but CMAKE_OBJDUMP was not found")
    endif()
endif()

# ==================================================
# Size 信息生成
# ==================================================
# 打印并保存目标文件段大小。
if(DEFINED TC_PRINT_SIZE AND TC_PRINT_SIZE)
    if(CMAKE_SIZE)
        set(SIZE_SCRIPT "${CMAKE_BINARY_DIR}/ck_size_to_file.cmake")

        file(WRITE "${SIZE_SCRIPT}"
            "execute_process(
                COMMAND \"\${CK_SIZE}\" --format=berkeley \"\${CK_INPUT_FILE}\"
                RESULT_VARIABLE _size_print_result
            )
            if(NOT _size_print_result EQUAL 0)
                message(FATAL_ERROR \"size print failed: \${_size_print_result}\")
            endif()

            execute_process(
                COMMAND \"\${CK_SIZE}\" -A \"\${CK_INPUT_FILE}\"
                OUTPUT_FILE \"\${CK_OUTPUT_FILE}\"
                RESULT_VARIABLE _size_save_result
            )
            if(NOT _size_save_result EQUAL 0)
                message(FATAL_ERROR \"size save failed: \${_size_save_result}\")
            endif()
        ")

        add_custom_command(
            OUTPUT ${SIZE_FILE}
            COMMAND ${CMAKE_COMMAND}
                "-DCK_SIZE=${CMAKE_SIZE}"
                "-DCK_INPUT_FILE=${TARGET_FILE}"
                "-DCK_OUTPUT_FILE=${SIZE_FILE}"
                -P "${SIZE_SCRIPT}"
            DEPENDS ${PRO_NAME}
            COMMENT "Printing and saving target section sizes"
            VERBATIM
        )

        add_custom_target(${PRO_NAME}_size ALL
            DEPENDS ${SIZE_FILE}
        )
    else()
        message(WARNING "TC_PRINT_SIZE is enabled, but CMAKE_SIZE was not found")
    endif()
endif()

# ==================================================
# 单元测试配置
# ==================================================
# 开启后会把当前目标注册为一个 CTest 测试项。
if(DEFINED CK_TEST_UNIT AND CK_TEST_UNIT)
    enable_testing()

    add_test(
        NAME ${PRO_NAME}_unit
        COMMAND $<TARGET_FILE:${PRO_NAME}>
    )

    message(STATUS "Registered unit test: ${PRO_NAME}_unit")
endif()

message(STATUS "========== Project configuration finished: ${PRO_NAME} ==========")
