# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2026-5-26
# Version: 2.4.0

# ==================================================
# CK 工程通用 CMake 函数
# ==================================================
# 本文件只封装可复用的细节函数。
# 平台关键流程仍然保留在各自工程的 CMakeLists.txt 中，避免构建路径被隐藏。

# ==================================================
# 基础工具函数
# ==================================================
# 设置变量默认值。
# 只有变量未定义时才会写入，避免覆盖 Kconfig 或工程手动配置。
macro(ck_set_default var_name default_value)
    if(NOT DEFINED ${var_name})
        set(${var_name} ${default_value})
    endif()
endmacro()

# 安全去重列表。
macro(ck_list_remove_duplicates var_name)
    if(DEFINED ${var_name} AND NOT "${${var_name}}" STREQUAL "")
        list(REMOVE_DUPLICATES ${var_name})
    endif()
endmacro()

# 将字符串配置转换为 CMake 列表。
# 支持 Kconfig / Python 生成的空格分隔字符串，也兼容 CMake 原生分号列表。
function(ck_string_to_list output_var input_value)
    if("${input_value}" STREQUAL "")
        set(${output_var} "" PARENT_SCOPE)
        return()
    endif()

    if("${input_value}" MATCHES ";")
        set(_result ${input_value})
    else()
        separate_arguments(_result NATIVE_COMMAND "${input_value}")
    endif()

    set(${output_var} ${_result} PARENT_SCOPE)
endfunction()

# 将路径列表统一解析为绝对路径。
function(ck_resolve_path_list output_var)
    set(_result "")

    foreach(dir ${ARGN})
        if(NOT "${dir}" STREQUAL "")
            get_filename_component(_abs_dir "${dir}" ABSOLUTE BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
            list(APPEND _result "${_abs_dir}")
        endif()
    endforeach()

    if(_result)
        list(REMOVE_DUPLICATES _result)
    endif()

    set(${output_var} ${_result} PARENT_SCOPE)
endfunction()

# 统一封装 target_link_libraries()。
# 默认使用 PRIVATE；遇到外部 CMake 使用 plain signature 时，可以切换为 plain。
function(ck_target_link_libraries target)
    if(NOT ARGN)
        return()
    endif()

    if(DEFINED CK_LINK_LIBRARIES_MODE AND CK_LINK_LIBRARIES_MODE STREQUAL "plain")
        target_link_libraries(${target} ${ARGN})
    else()
        target_link_libraries(${target} PRIVATE ${ARGN})
    endif()
endfunction()


# ==================================================
# 工程开始与结束打印
# ==================================================
# 打印工程开始信息。
macro(ck_project_begin target)
    message(STATUS "========== Start project configuration: ${target} ==========")

    if(COMMAND print_paths)
        print_paths()
    endif()
endmacro()

# 打印工程结束信息。
macro(ck_project_end target)
    message(STATUS "========== Project configuration finished: ${target} ==========")
endmacro()


# ==================================================
# Profile 默认配置
# ==================================================
# 通用工程默认配置。
macro(ck_profile_generic)
    ck_set_default(CK_PROJECT_TYPE "generic")
    ck_set_default(CK_LINK_LIBRARIES_MODE "scoped")
    ck_set_default(CK_TARGET_SUFFIX "")

    if(NOT DEFINED CK_EXCLUDE_DIRS)
        set(CK_EXCLUDE_DIRS
            build
            bin
        )
    endif()

    ck_set_default(TC_GENERATE_MAP_FILE OFF)
    ck_set_default(TC_PRINT_MEMORY_USAGE OFF)
    ck_set_default(TC_GENERATE_BIN OFF)
    ck_set_default(TC_GENERATE_DISASSEMBLY OFF)
    ck_set_default(TC_PRINT_SIZE OFF)
endmacro()

# 通用 MCU 工程默认配置。
# 适合 GD32 / CH32 / NXP / 裸机 ARM 等非 CubeMX 工程作为起点。
macro(ck_profile_mcu)
    ck_set_default(CK_PROJECT_TYPE "mcu")
    ck_set_default(CK_LINK_LIBRARIES_MODE "scoped")
    ck_set_default(CK_TARGET_SUFFIX ".elf")

    if(NOT DEFINED CK_EXCLUDE_DIRS)
        set(CK_EXCLUDE_DIRS
            build
            bin
        )
    endif()

    ck_set_default(TC_GENERATE_MAP_FILE ON)
    ck_set_default(TC_PRINT_MEMORY_USAGE ON)
    ck_set_default(TC_GENERATE_BIN ON)
    ck_set_default(TC_GENERATE_DISASSEMBLY ON)
    ck_set_default(TC_PRINT_SIZE ON)
endmacro()

# STM32 CubeMX 工程默认配置。
macro(ck_profile_stm32)
    ck_set_default(CK_PROJECT_TYPE "stm32")
    ck_set_default(CK_LINK_LIBRARIES_MODE "plain")
    ck_set_default(CK_TARGET_SUFFIX ".elf")

    if(NOT DEFINED CK_EXCLUDE_DIRS)
        set(CK_EXCLUDE_DIRS
            build
            bin
            cmake
            Core
            Drivers
        )
    endif()

    ck_set_default(TC_GENERATE_MAP_FILE ON)
    ck_set_default(TC_PRINT_MEMORY_USAGE ON)
    ck_set_default(TC_GENERATE_BIN ON)
    ck_set_default(TC_GENERATE_DISASSEMBLY ON)
    ck_set_default(TC_PRINT_SIZE ON)
endmacro()

# Linux 应用工程默认配置。
macro(ck_profile_linux_app)
    ck_set_default(CK_PROJECT_TYPE "linux_app")
    ck_set_default(CK_LINK_LIBRARIES_MODE "scoped")
    ck_set_default(CK_TARGET_SUFFIX "")

    if(NOT DEFINED CK_EXCLUDE_DIRS)
        set(CK_EXCLUDE_DIRS
            build
            bin
        )
    endif()

    ck_set_default(TC_GENERATE_MAP_FILE OFF)
    ck_set_default(TC_PRINT_MEMORY_USAGE OFF)
    ck_set_default(TC_GENERATE_BIN OFF)
    ck_set_default(TC_GENERATE_DISASSEMBLY OFF)
    ck_set_default(TC_PRINT_SIZE OFF)
endmacro()

# 归一化工程默认配置。
# Profile 设置差异，本函数只负责兜底、去重和打印。
macro(ck_project_set_defaults)
    ck_set_default(CK_PROJECT_TYPE "generic")
    ck_set_default(CK_LINK_LIBRARIES_MODE "scoped")
    ck_set_default(CK_TARGET_SUFFIX "")

    if(NOT DEFINED CK_EXCLUDE_DIRS)
        set(CK_EXCLUDE_DIRS
            build
            bin
        )
    endif()

    ck_set_default(TC_GENERATE_MAP_FILE OFF)
    ck_set_default(TC_PRINT_MEMORY_USAGE OFF)
    ck_set_default(TC_GENERATE_BIN OFF)
    ck_set_default(TC_GENERATE_DISASSEMBLY OFF)
    ck_set_default(TC_PRINT_SIZE OFF)

    ck_list_remove_duplicates(CK_EXCLUDE_DIRS)

    message(STATUS "Project type: ${CK_PROJECT_TYPE}")
    message(STATUS "Link libraries mode: ${CK_LINK_LIBRARIES_MODE}")
    message(STATUS "Target suffix: ${CK_TARGET_SUFFIX}")
    message(STATUS "Excluded directories: ${CK_EXCLUDE_DIRS}")
endmacro()


# ==================================================
# 输出目录与目标定义
# ==================================================
# 设置构建输出目录。
macro(ck_set_output_dirs)
    set(options)
    set(oneValueArgs OUTPUT_DIR)
    set(multiValueArgs)
    cmake_parse_arguments(CK_OUT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(CK_OUT_OUTPUT_DIR)
        set(OUTPUT_DIR "${CK_OUT_OUTPUT_DIR}")
    elseif(DEFINED CK_OUTPUT_DIR AND NOT "${CK_OUTPUT_DIR}" STREQUAL "")
        set(OUTPUT_DIR "${CK_OUTPUT_DIR}")
    else()
        set(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")
    endif()

    if(NOT IS_ABSOLUTE "${OUTPUT_DIR}")
        get_filename_component(OUTPUT_DIR "${OUTPUT_DIR}" ABSOLUTE BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
    endif()

    file(MAKE_DIRECTORY "${OUTPUT_DIR}")

    # 可执行文件输出目录，例如 .elf / .exe。
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${OUTPUT_DIR}")

    # 动态库输出目录，例如 .dll / .so / .dylib。
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${OUTPUT_DIR}")

    # 静态库输出目录，例如 .a / .lib。
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${OUTPUT_DIR}")

    message(STATUS "Build output directory: ${OUTPUT_DIR}")
endmacro()

# 创建可执行目标。
macro(ck_create_target target)
    if(NOT TARGET ${target})
        add_executable(${target})
    endif()

    if(DEFINED CK_TARGET_SUFFIX AND NOT "${CK_TARGET_SUFFIX}" STREQUAL "")
        set_target_properties(${target} PROPERTIES
            SUFFIX "${CK_TARGET_SUFFIX}"
        )
    endif()
endmacro()


# ==================================================
# Kconfig 外部模块扫描
# ==================================================
# 从 Kconfig 中的 CK_TOOL_EXTERNAL_START / CK_TOOL_EXTERNAL_END 区间添加外部模块路径。
function(ck_add_kconfig_external_paths kconfig_file)
    if(NOT EXISTS "${kconfig_file}")
        message(WARNING "Kconfig file not found, no external paths added: ${kconfig_file}")
        return()
    endif()

    file(STRINGS "${kconfig_file}" _kconfig_lines)
    set(_inside_external_block FALSE)
    set(_external_count 0)

    foreach(_line IN LISTS _kconfig_lines)
        if(_line MATCHES "^[ \t]*#[ \t]*CK_TOOL_EXTERNAL_START[ \t]*$")
            set(_inside_external_block TRUE)
        elseif(_line MATCHES "^[ \t]*#[ \t]*CK_TOOL_EXTERNAL_END[ \t]*$")
            set(_inside_external_block FALSE)
        elseif(_inside_external_block AND _line MATCHES "^[ \t]*source[ \t]+\"([^\"]+)/Kconfig\"[ \t]*$")
            set(_external_source_dir "${CMAKE_MATCH_1}")
            string(REGEX MATCHALL "\\$\\([A-Za-z_][A-Za-z0-9_]*\\)" _external_vars "${_external_source_dir}")

            foreach(_external_var IN LISTS _external_vars)
                string(REGEX REPLACE "^\\$\\(([A-Za-z_][A-Za-z0-9_]*)\\)$" "\\1" _external_var_name "${_external_var}")

                if(NOT DEFINED ${_external_var_name})
                    message(FATAL_ERROR "Undefined Kconfig path variable in external source: ${_external_var_name}")
                endif()

                string(REPLACE "${_external_var}" "${${_external_var_name}}" _external_source_dir "${_external_source_dir}")
            endforeach()

            get_filename_component(_external_binary_name "${_external_source_dir}" NAME)
            if("${_external_binary_name}" STREQUAL "")
                message(FATAL_ERROR "Unable to derive external build directory from: ${_line}")
            endif()

            set_external_path("${_external_source_dir}" "${_external_binary_name}")
            math(EXPR _external_count "${_external_count} + 1")
        endif()
    endforeach()

    if(_inside_external_block)
        message(FATAL_ERROR "Missing CK_TOOL_EXTERNAL_END in ${kconfig_file}")
    endif()

    if(_external_count EQUAL 0)
        message(STATUS "No external module source entries found in ${kconfig_file}")
    endif()
endfunction()


# ==================================================
# 工程扫描函数
# ==================================================
# 搜索当前工程目录下的源文件。
macro(ck_collect_current_sources)
    if(COMMAND find_current_source_file)
        find_current_source_file()
    else()
        message(WARNING "find_current_source_file() is not defined")
    endif()
endmacro()

# 搜索当前工程目录下的头文件路径。
macro(ck_collect_current_includes)
    if(COMMAND find_current_header_dir)
        find_current_header_dir()
    else()
        message(WARNING "find_current_header_dir() is not defined")
    endif()
endmacro()

# 从 Kconfig 外部模块配置入口自动添加构建搜索路径。
macro(ck_collect_kconfig_external_paths)
    set(options)
    set(oneValueArgs KCONFIG_FILE)
    set(multiValueArgs)
    cmake_parse_arguments(CK_EXT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(CK_EXT_KCONFIG_FILE)
        ck_add_kconfig_external_paths("${CK_EXT_KCONFIG_FILE}")
    else()
        ck_add_kconfig_external_paths("${CMAKE_CURRENT_SOURCE_DIR}/Kconfig")
    endif()
endmacro()

# 搜索当前目录下一层 CMake 模块。
macro(ck_collect_cmake_subdirs)
    if(COMMAND find_cmakelists_current_dir)
        find_cmakelists_current_dir(${CK_EXCLUDE_DIRS})
    else()
        message(WARNING "find_cmakelists_current_dir() is not defined")
    endif()
endmacro()

# 收集并打印所有源文件、头文件路径和库文件。
macro(ck_collect_print_project_files)
    if(COMMAND print_all_code_sources)
        print_all_code_sources(SRC_FILES)
    endif()

    if(COMMAND print_all_code_includes)
        print_all_code_includes(INCLUDE_PATH)
    endif()

    if(COMMAND print_all_code_librarys)
        print_all_code_librarys(LIB_FILES)
    endif()
endmacro()

# 统一去重源码、头文件路径和库文件。
macro(ck_normalize_project_files)
    ck_list_remove_duplicates(SRC_FILES)
    ck_list_remove_duplicates(INCLUDE_PATH)
    ck_list_remove_duplicates(LIB_FILES)
endmacro()


# ==================================================
# 目标源码和头文件配置
# ==================================================
# 将收集到的源码加入主目标。
function(ck_target_apply_sources target)
    if(DEFINED SRC_FILES AND NOT "${SRC_FILES}" STREQUAL "")
        target_sources(${target}
            PRIVATE
                ${SRC_FILES}
        )
    endif()
endfunction()

# 将收集到的头文件路径加入主目标。
function(ck_target_apply_includes target)
    if(DEFINED INCLUDE_PATH AND NOT "${INCLUDE_PATH}" STREQUAL "")
        target_include_directories(${target}
            PRIVATE
                ${INCLUDE_PATH}
        )
    endif()
endfunction()


# ==================================================
# 工具链编译配置
# ==================================================
# 添加工具链或 Kconfig 配置中的库搜索路径。
function(ck_target_apply_library_dirs target)
    if(DEFINED TC_LIBRARY_DIRS AND NOT "${TC_LIBRARY_DIRS}" STREQUAL "")
        ck_string_to_list(_tc_library_dirs "${TC_LIBRARY_DIRS}")
        ck_resolve_path_list(_resolved_lib_dirs ${_tc_library_dirs})

        if(_resolved_lib_dirs)
            target_link_directories(${target}
                PRIVATE
                    ${_resolved_lib_dirs}
            )

            message(STATUS "Added library search paths: ${_resolved_lib_dirs}")
        endif()
    endif()
endfunction()

# 添加工具链或 Kconfig 配置中的宏定义。
function(ck_target_apply_definitions target)
    if(DEFINED TC_DEFINE_MACROS AND NOT "${TC_DEFINE_MACROS}" STREQUAL "")
        ck_string_to_list(_tc_define_macros "${TC_DEFINE_MACROS}")

        if(_tc_define_macros)
            target_compile_definitions(${target}
                PRIVATE
                    ${_tc_define_macros}
            )

            message(STATUS "Added compile definitions: ${_tc_define_macros}")
        endif()
    endif()
endfunction()


# ==================================================
# 链接库配置
# ==================================================
# 添加工具链或 Kconfig 配置中的链接库。
function(ck_target_apply_toolchain_libraries target)
    if(DEFINED TC_LINK_LIBRARIES AND NOT "${TC_LINK_LIBRARIES}" STREQUAL "")
        ck_string_to_list(_tc_link_libraries "${TC_LINK_LIBRARIES}")

        if(_tc_link_libraries)
            ck_target_link_libraries(${target} ${_tc_link_libraries})
            message(STATUS "Added toolchain link libraries: ${_tc_link_libraries}")
        endif()
    endif()
endfunction()

# 添加工程扫描到的库文件。
function(ck_target_apply_project_libraries target)
    if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
        ck_target_link_libraries(${target} ${LIB_FILES})
        message(STATUS "Added project library files: ${LIB_FILES}")
    endif()
endfunction()


# ==================================================
# Binutils 工具查找
# ==================================================
# 根据 CMAKE_C_COMPILER 尝试推导工具链前缀。
function(ck_get_toolchain_prefix output_var)
    set(_prefix "")

    if(DEFINED CMAKE_C_COMPILER AND NOT "${CMAKE_C_COMPILER}" STREQUAL "")
        get_filename_component(_compiler_name "${CMAKE_C_COMPILER}" NAME_WE)

        set(_try_prefix "${_compiler_name}")
        string(REGEX REPLACE "(-gcc|-g\\+\\+|-clang|-clang\\+\\+|-cc)$" "" _try_prefix "${_try_prefix}")

        if(NOT "${_try_prefix}" STREQUAL "${_compiler_name}")
            set(_prefix "${_try_prefix}")
        endif()
    endif()

    set(${output_var} "${_prefix}" PARENT_SCOPE)
endfunction()

# 尝试查找 binutils 工具。
# 优先使用工具链文件显式提供的 CMAKE_xxx，其次从编译器同目录查找，最后从 PATH 查找。
function(ck_find_binutils_tool output_var)
    set(options)
    set(oneValueArgs TOOL_NAME FALLBACK_NAME)
    set(multiValueArgs NAMES)
    cmake_parse_arguments(CK_TOOL "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(DEFINED ${output_var} AND NOT "${${output_var}}" STREQUAL "")
        return()
    endif()

    set(_tool_names "")

    if(CK_TOOL_TOOL_NAME)
        ck_get_toolchain_prefix(_toolchain_prefix)

        if(_toolchain_prefix)
            list(APPEND _tool_names "${_toolchain_prefix}-${CK_TOOL_TOOL_NAME}")
        endif()

        list(APPEND _tool_names "${CK_TOOL_TOOL_NAME}")
    endif()

    if(CK_TOOL_NAMES)
        list(APPEND _tool_names ${CK_TOOL_NAMES})
    endif()

    if(_tool_names)
        list(REMOVE_DUPLICATES _tool_names)
    else()
        message(WARNING "No tool names provided for ${output_var}")
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
            NAMES ${_tool_names}
            HINTS ${_tool_hints}
            NO_DEFAULT_PATH
        )
    endif()

    if(NOT DEFINED ${output_var} OR "${${output_var}}" STREQUAL "")
        find_program(${output_var}
            NAMES ${_tool_names}
        )
    endif()

    if(DEFINED ${output_var} AND NOT "${${output_var}}" STREQUAL "")
        set(${output_var} "${${output_var}}" PARENT_SCOPE)
    elseif(CK_TOOL_FALLBACK_NAME)
        message(STATUS "${output_var} not found, ${CK_TOOL_FALLBACK_NAME} generation will be skipped if enabled")
    endif()
endfunction()

# 打印常用 binutils 工具路径。
macro(ck_print_binutils_tools)
    message(STATUS "CMAKE_OBJCOPY = ${CMAKE_OBJCOPY}")
    message(STATUS "CMAKE_OBJDUMP = ${CMAKE_OBJDUMP}")
    message(STATUS "CMAKE_SIZE    = ${CMAKE_SIZE}")
endmacro()


# ==================================================
# 构建产物生成
# ==================================================
# 生成 map 文件。
function(ck_target_enable_map target)
    if(DEFINED TC_GENERATE_MAP_FILE AND TC_GENERATE_MAP_FILE)
        set(MAP_FILE "${OUTPUT_DIR}/${target}.map")

        if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
            message(STATUS "Map file will be generated at: ${MAP_FILE}")

            target_link_options(${target}
                PRIVATE
                    "-Wl,-Map=${MAP_FILE}"
                    "-Wl,--cref"
            )

            if(DEFINED TC_PRINT_MEMORY_USAGE AND TC_PRINT_MEMORY_USAGE)
                target_link_options(${target}
                    PRIVATE
                        "-Wl,--print-memory-usage"
                )
            endif()
        else()
            message(WARNING "TC_GENERATE_MAP_FILE is enabled, but current compiler may not support GNU map options")
        endif()
    endif()
endfunction()

# 生成裸 bin 文件。
function(ck_target_generate_bin target)
    if(DEFINED TC_GENERATE_BIN AND TC_GENERATE_BIN)
        if(CMAKE_OBJCOPY)
            set(BIN_FILE "${OUTPUT_DIR}/${target}.bin")

            add_custom_command(
                OUTPUT "${BIN_FILE}"
                COMMAND ${CMAKE_COMMAND} -E make_directory "${OUTPUT_DIR}"
                COMMAND "${CMAKE_OBJCOPY}" -O binary "$<TARGET_FILE:${target}>" "${BIN_FILE}"
                DEPENDS ${target}
                COMMENT "Generating binary file: ${target}.bin"
                VERBATIM
            )

            add_custom_target(${target}_bin ALL
                DEPENDS "${BIN_FILE}"
            )
        else()
            message(WARNING "TC_GENERATE_BIN is enabled, but CMAKE_OBJCOPY was not found")
        endif()
    endif()
endfunction()

# 生成反汇编文件。
function(ck_target_generate_disassembly target)
    if(DEFINED TC_GENERATE_DISASSEMBLY AND TC_GENERATE_DISASSEMBLY)
        if(CMAKE_OBJDUMP)
            set(DIS_FILE "${OUTPUT_DIR}/${target}.dis")
            set(OBJDUMP_SCRIPT "${CMAKE_BINARY_DIR}/ck_objdump_to_file.cmake")

            file(WRITE "${OBJDUMP_SCRIPT}" [=[
execute_process(
    COMMAND "${CK_OBJDUMP}" -D "${CK_INPUT_FILE}"
    OUTPUT_FILE "${CK_OUTPUT_FILE}"
    RESULT_VARIABLE _objdump_result
)

if(NOT _objdump_result EQUAL 0)
    message(FATAL_ERROR "objdump failed: ${_objdump_result}")
endif()
]=])

            add_custom_command(
                OUTPUT "${DIS_FILE}"
                COMMAND ${CMAKE_COMMAND}
                    "-DCK_OBJDUMP=${CMAKE_OBJDUMP}"
                    "-DCK_INPUT_FILE=$<TARGET_FILE:${target}>"
                    "-DCK_OUTPUT_FILE=${DIS_FILE}"
                    -P "${OBJDUMP_SCRIPT}"
                DEPENDS ${target}
                COMMENT "Generating disassembly file: ${target}.dis"
                VERBATIM
            )

            add_custom_target(${target}_dis ALL
                DEPENDS "${DIS_FILE}"
            )
        else()
            message(WARNING "TC_GENERATE_DISASSEMBLY is enabled, but CMAKE_OBJDUMP was not found")
        endif()
    endif()
endfunction()

# 打印并保存目标文件段大小。
function(ck_target_generate_size target)
    if(DEFINED TC_PRINT_SIZE AND TC_PRINT_SIZE)
        if(CMAKE_SIZE)
            set(SIZE_FILE "${OUTPUT_DIR}/${target}.size.txt")
            set(SIZE_SCRIPT "${CMAKE_BINARY_DIR}/ck_size_to_file.cmake")

            file(WRITE "${SIZE_SCRIPT}" [=[
execute_process(
    COMMAND "${CK_SIZE}" --format=berkeley "${CK_INPUT_NAME}"
    WORKING_DIRECTORY "${CK_WORK_DIR}"
    RESULT_VARIABLE _size_print_result
)

if(NOT _size_print_result EQUAL 0)
    message(FATAL_ERROR "size print failed: ${_size_print_result}")
endif()

execute_process(
    COMMAND "${CK_SIZE}" -A "${CK_INPUT_NAME}"
    WORKING_DIRECTORY "${CK_WORK_DIR}"
    OUTPUT_FILE "${CK_OUTPUT_FILE}"
    RESULT_VARIABLE _size_save_result
)

if(NOT _size_save_result EQUAL 0)
    message(FATAL_ERROR "size save failed: ${_size_save_result}")
endif()
]=])

            add_custom_command(
                OUTPUT "${SIZE_FILE}"
                COMMAND ${CMAKE_COMMAND}
                    "-DCK_SIZE=${CMAKE_SIZE}"
                    "-DCK_WORK_DIR=${OUTPUT_DIR}"
                    "-DCK_INPUT_NAME=$<TARGET_FILE_NAME:${target}>"
                    "-DCK_OUTPUT_FILE=${SIZE_FILE}"
                    -P "${SIZE_SCRIPT}"
                DEPENDS ${target}
                COMMENT "Printing and saving target section sizes"
                VERBATIM
            )

            add_custom_target(${target}_size ALL
                DEPENDS "${SIZE_FILE}"
            )
        else()
            message(WARNING "TC_PRINT_SIZE is enabled, but CMAKE_SIZE was not found")
        endif()
    endif()
endfunction()


# ==================================================
# 单元测试配置
# ==================================================
# 开启后会把当前目标注册为一个 CTest 测试项。
function(ck_target_enable_test target)
    if(DEFINED CK_TEST_UNIT AND CK_TEST_UNIT)
        enable_testing()

        add_test(
            NAME ${target}_unit
            COMMAND $<TARGET_FILE:${target}>
        )

        message(STATUS "Registered unit test: ${target}_unit")
    endif()
endfunction()
