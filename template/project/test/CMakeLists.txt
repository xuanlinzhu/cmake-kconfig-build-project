# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2025-6-28
# Version: 2.0.0
############################标准设置，不修改###################################
# 设置cmake最小要求版本
cmake_minimum_required(VERSION 3.10)

# 引入kconfig配置
include(ck_config.cmake)
# 引入cmakelib
include(${CK_TOOLS_ROOT}/ck_tools/ck_cmlib.cmake)
# 引入工具链配置
include(${CK_TOOLS_ROOT}/ck_tools/ck_toolchain.cmake)

# 工程名字
project(${PRO_NAME})

message("---------------开始构建----------------")
print_paths()

# 设置输出路径
set(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")
# 控制生成的可执行文件（例如：.exe 文件）的输出目录。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})
#控制生成的共享库（例如：.dll 文件）的输出目录
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR})
#控制生成的静态库（例如：.lib 文件）的输出目录。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR})

############################用户设置，可修改###################################

# 寻找当前文件夹的源文件
find_current_source_file()
find_current_header_dir()

# 配置外部工程路径
set_external_path("${CK_WORKSPACE_ROOT}/package" "package")
set_external_path("${CK_WORKSPACE_ROOT}/driver" "driver")

############################标准设置，不修改###################################

# 添加链接库路径
if(DEFINED TC_LIBRARY_DIRS AND NOT TC_LIBRARY_DIRS STREQUAL "")
    string(REPLACE " " ";" TC_LIBRARY_DIRS_LIST "${TC_LIBRARY_DIRS}")

    set(_resolved_lib_dirs "")
    foreach(dir ${TC_LIBRARY_DIRS_LIST})
        # 将每个路径转换为绝对路径（相对路径会基于当前CMakeLists.txt解析）
        get_filename_component(abs_dir "${dir}" REALPATH BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
        list(APPEND _resolved_lib_dirs "${abs_dir}")
    endforeach()

    link_directories(${_resolved_lib_dirs})

    message(STATUS "Added library paths (resolved): ${_resolved_lib_dirs}")
endif()

# 排除搜索路径
find_cmakelists_current_dir("build" "bin")

print_all_code_sources(SRC_FILES)

set_source_files_properties(${SRC_FILES} PROPERTIES LANGUAGE C)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

INCLUDE_DIRECTORIES(${INCLUDE_PATH})

add_executable(${PRO_NAME} ${SRC_FILES})

# 添加预定义宏
if(DEFINED TC_DEFINE_MACROS AND NOT TC_DEFINE_MACROS STREQUAL "")
    # 将空格分隔的宏列表转换成 CMake 列表
    string(REPLACE " " ";" TC_DEFINE_MACROS_LIST "${TC_DEFINE_MACROS}")

    target_compile_definitions(${PRO_NAME} PUBLIC ${TC_DEFINE_MACROS_LIST})

    message(STATUS "Added macro definitions: ${TC_DEFINE_MACROS}")
endif()

# 添加链接库
if(DEFINED TC_LINK_LIBRARIES AND NOT TC_LINK_LIBRARIES STREQUAL "")
    # 把空格分隔的字符串转换成CMake列表
    string(REPLACE " " ";" TC_LINK_LIBRARIES_LIST "${TC_LINK_LIBRARIES}")

    # 这里举例添加为编译选项（你也可以换成链接选项或其他）
    target_link_libraries(${PRO_NAME} PRIVATE ${TC_LINK_LIBRARIES_LIST})

    message(STATUS "Added link libraries options: ${TC_LINK_LIBRARIES}")
endif()

# bin 文件生成
if(DEFINED TC_GENERATE_BIN)
        add_custom_command(TARGET ${PRO_NAME} POST_BUILD
        COMMAND ${TC_C_CXX_COMPILER}-objcopy -O binary $<TARGET_FILE:${PRO_NAME}> ${OUTPUT_DIR}/${PRO_NAME}.bin
        COMMENT "Generating binary file: ${PRO_NAME}.bin"
        )
endif()

# 反汇编文件生成
if(DEFINED TC_GENERATE_DISASSEMBLY)
    if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
        add_custom_command(TARGET ${PRO_NAME} POST_BUILD
            COMMAND cmd /c "${TC_C_CXX_COMPILER}-objdump -D $<TARGET_FILE:${PRO_NAME}> > ${OUTPUT_DIR}\\${PRO_NAME}.dis"
            COMMENT "Generating disassembly file [win]: ${PRO_NAME}.dis"
        )
    else()
        add_custom_command(TARGET ${PRO_NAME} POST_BUILD
            COMMAND /bin/sh -c '${TC_C_CXX_COMPILER}-objdump -D $<TARGET_FILE:${PRO_NAME}> > ${OUTPUT_DIR}/${PRO_NAME}.dis'
            COMMENT "Generating disassembly file [linux]: ${PRO_NAME}.dis"
        )
    endif()
endif()

# map文件生成
if(TC_GENERATE_MAP_FILE)
    message(STATUS "Map file will be generated at: ${CMAKE_BINARY_DIR}/bin/${PRO_NAME}.map")
    target_link_options(${PRO_NAME} PRIVATE
        "-Wl,-Map=${OUTPUT_DIR}/${PRO_NAME}.map"
        "-Wl,-cref"
    )
endif()

# 链接库
if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    target_link_libraries(${PRO_NAME} ${LIB_FILES})
endif()
