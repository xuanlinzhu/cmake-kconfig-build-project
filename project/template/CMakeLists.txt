# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2025-6-28
# Version: 2.0.0
############################标准设置，不修改###################################
# 设置cmake最小要求版本
cmake_minimum_required(VERSION 3.5)

# 引入kconfig配置
include(ck_config.cmake)
# 引入cmakelib
include(${ROOT_PATH}/tools/script/ck_cmlib.cmake)
# 引入工具链配置
include(${ROOT_PATH}/tools/script/ck_toolchain.cmake)

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
set_external_path("${ROOT_PATH}/package" "package")
set_external_path("${ROOT_PATH}/driver" "driver")


############################标准设置，不修改###################################

# 排除搜索路径
find_cmakelists_current_dir("build" "bin")

print_all_code_sources(SRC_FILES)

set_source_files_properties(${SRC_FILES} PROPERTIES LANGUAGE C)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

INCLUDE_DIRECTORIES(${INCLUDE_PATH})

add_executable(${PRO_NAME} ${SRC_FILES})

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
