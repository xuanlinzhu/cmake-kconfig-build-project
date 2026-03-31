cmake_minimum_required(VERSION 3.22)

# 引入kconfig配置
include(ck_config.cmake)
# 引入cmakelib
include(${CK_TOOLS_PATH}/ck_tools/ck_cmlib.cmake)

# --------------------------------------------------
# 基础设置
# --------------------------------------------------
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

# 工程名
set(CMAKE_PROJECT_NAME ${PRO_NAME})

project(${CMAKE_PROJECT_NAME})
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

enable_language(C ASM)

message("---------------开始构建----------------")
print_paths()

# --------------------------------------------------
# 输出目录
# --------------------------------------------------
set(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR})

# --------------------------------------------------
# 创建主目标
# --------------------------------------------------
add_executable(${CMAKE_PROJECT_NAME})

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
# 不再用 INCLUDE_DIRECTORIES，全改为 target 级
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
# 先链接 CubeMX，再链接你的库
# --------------------------------------------------
target_link_libraries(${CMAKE_PROJECT_NAME}
    stm32cubemx
)

if(DEFINED LIB_FILES AND NOT "${LIB_FILES}" STREQUAL "")
    list(REMOVE_DUPLICATES LIB_FILES)
    target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE ${LIB_FILES})
endif()

# --------------------------------------------------
# 生成 bin / dis / map
# 这里沿用你原来的逻辑
# --------------------------------------------------
add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
    COMMAND ${TC_C_CXX_COMPILER}-objcopy -O binary
            $<TARGET_FILE:${CMAKE_PROJECT_NAME}>
            ${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.bin
    COMMENT "Generating binary file: ${CMAKE_PROJECT_NAME}.bin"
)



if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
    add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
        COMMAND cmd /c "${TC_C_CXX_COMPILER}-objdump -D $<TARGET_FILE:${CMAKE_PROJECT_NAME}> > ${OUTPUT_DIR}\\${CMAKE_PROJECT_NAME}.dis"
        COMMENT "Generating disassembly file [win]: ${CMAKE_PROJECT_NAME}.dis"
    )
else()
    add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD
        COMMAND /bin/sh -c "${TC_C_CXX_COMPILER}-objdump -D $<TARGET_FILE:${CMAKE_PROJECT_NAME}> > ${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.dis"
        COMMENT "Generating disassembly file [linux]: ${CMAKE_PROJECT_NAME}.dis"
    )
endif()



# message(STATUS "Map file will be generated at: ${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.map")
# target_link_options(${CMAKE_PROJECT_NAME} PRIVATE
#     "-Wl,-Map=${OUTPUT_DIR}/${CMAKE_PROJECT_NAME}.map"
#     "-Wl,-cref"
# )
