cmake_minimum_required(VERSION 3.22)

# 引入 kconfig 配置
include(ck_config.cmake)
# 引入 cmakelib
include(${CK_TOOLS_PATH}/ck_tools/ck_cmlib.cmake)

# --------------------------------------------------
# 基础设置
# --------------------------------------------------
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 工程名
set(CMAKE_PROJECT_NAME ${PRO_NAME})

project(${CMAKE_PROJECT_NAME} C ASM)

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Start build...")

print_paths()

# --------------------------------------------------
# 输出目录
# --------------------------------------------------
set(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")
file(MAKE_DIRECTORY ${OUTPUT_DIR})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR})

# --------------------------------------------------
# 创建主目标
# --------------------------------------------------
add_executable(${CMAKE_PROJECT_NAME})

# 让输出文件名固定为 xxx.elf
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES SUFFIX ".elf")

# --------------------------------------------------
# CubeMX 生成部分
# --------------------------------------------------
add_subdirectory(cmake/stm32cubemx)

# 外部模块
set_external_path("${PRO_TOP_PATH}/package" "package")
set_external_path("${PRO_TOP_PATH}/driver" "driver")

# 遍历当前目录下一级模块，但排除 CubeMX 相关目录
find_cmakelists_current_dir("build" "bin" "cmake" "Core" "Drivers")

print_all_code_sources(SRC_FILES)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

# --------------------------------------------------
# 把收集到的源码加入主目标
# --------------------------------------------------
if(DEFINED SRC_FILES AND NOT "${SRC_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES SRC_FILES)
    set_source_files_properties(${SRC_FILES} PROPERTIES LANGUAGE C)
    target_sources(${CMAKE_PROJECT_NAME} PRIVATE ${SRC_FILES})
endif()

# --------------------------------------------------
# 把收集到的头文件路径加入主目标
# --------------------------------------------------
if(DEFINED INCLUDE_PATH AND NOT "${INCLUDE_PATH}" STREQUAL "")
    list(REMOVE_DUPLICATES INCLUDE_PATH)
    target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE ${INCLUDE_PATH})
endif()

# --------------------------------------------------
# 清理错误依赖
# --------------------------------------------------
list(REMOVE_ITEM CMAKE_C_IMPLICIT_LINK_LIBRARIES ob)

# --------------------------------------------------
# 链接库
# --------------------------------------------------
target_link_libraries(${CMAKE_PROJECT_NAME}
    stm32cubemx
)

if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES LIB_FILES)
    target_link_libraries(${CMAKE_PROJECT_NAME} ${LIB_FILES})
endif()

# --------------------------------------------------
# 工具查找
# 优先使用 CMake 已识别工具，否则自己推导
# --------------------------------------------------
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
# 生成 map 文件
# map 文件必须在链接阶段生成
# --------------------------------------------------
target_link_options(${CMAKE_PROJECT_NAME} PRIVATE
    "-Wl,-Map=${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.map"
    "-Wl,--cref"
    "-Wl,--print-memory-usage"
)

# --------------------------------------------------
# 生成 bin / dis / 打印段大小
# --------------------------------------------------
if(CMAKE_OBJCOPY)
    add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_OBJCOPY}
                -O binary
                $<TARGET_FILE:${CMAKE_PROJECT_NAME}>
                ${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.bin
        COMMENT "Generate binary file"
        VERBATIM
    )
endif()

if(CMAKE_OBJDUMP)
    if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
        add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
            COMMAND cmd /c
                    "\"${CMAKE_OBJDUMP}\" -D \"$<TARGET_FILE:${CMAKE_PROJECT_NAME}>\" > \"${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.dis\""
            COMMENT "Generate disassembly file"
            VERBATIM
        )
    else()
        add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
            COMMAND /bin/sh -c
                    "\"${CMAKE_OBJDUMP}\" -D \"$<TARGET_FILE:${CMAKE_PROJECT_NAME}>\" > \"${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.dis\""
            COMMENT "Generate disassembly file"
            VERBATIM
        )
    endif()
endif()

if(CMAKE_SIZE)
    add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_SIZE} --format=berkeley $<TARGET_FILE:${CMAKE_PROJECT_NAME}>
        COMMAND ${CMAKE_SIZE} -A $<TARGET_FILE:${CMAKE_PROJECT_NAME}>
        COMMENT "Print ELF section sizes"
        VERBATIM
    )
endif()
