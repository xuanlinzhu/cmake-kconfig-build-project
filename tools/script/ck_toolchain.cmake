# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2025-6-28
# Version: 2.0.0

message(STATUS "***************************** TOOLCHAIN START *****************************")
# System
if(DEFINED TC_SYSTEM_NAME_GENERIC )
    set(CMAKE_SYSTEM_NAME Generic)
elseif(DEFINED TC_SYSTEM_NAME_WINDOWS )
    set(CMAKE_SYSTEM_NAME Windows)
elseif(DEFINED TC_SYSTEM_NAME_LINUX )
    set(CMAKE_SYSTEM_NAME Linux)
elseif(DEFINED TC_SYSTEM_NAME_DARWIN )
    set(CMAKE_SYSTEM_NAME Darwin)
endif()

message(STATUS "Target System Type: ${CMAKE_SYSTEM_NAME}")

if(DEFINED TC_CPU_X86_64)
    set(CMAKE_SYSTEM_PROCESSOR "x86_64")
elseif(DEFINED TC_CPU_ARM)
    set(CMAKE_SYSTEM_PROCESSOR "arm")
elseif(DEFINED TC_CPU_AARCH64)
    set(CMAKE_SYSTEM_PROCESSOR "aarch64")
elseif(DEFINED TC_CPU_MIPS)
    set(CMAKE_SYSTEM_PROCESSOR "mips")
elseif(DEFINED TC_CPU_RISCV64)
    set(CMAKE_SYSTEM_PROCESSOR "riscv64")
endif()

message(STATUS "Target CPU Architecture: ${CMAKE_SYSTEM_PROCESSOR}")


if(DEFINED TC_BUILD_TYPE_DEBUG)
    set(CMAKE_BUILD_TYPE "Debug")
elseif(DEFINED TC_BUILD_TYPE_RELEASE)
    set(CMAKE_BUILD_TYPE "Release")
elseif(DEFINED TC_BUILD_TYPE_RELWITHDEBINFO)
    set(CMAKE_BUILD_TYPE "RelWithDebInfo")
elseif(DEFINED TC_BUILD_TYPE_MINSIZEREL)
    set(CMAKE_BUILD_TYPE "MinSizeRel")
endif()

message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")


if(DEFINED TC_CROSSCOMPILING )
    set(CMAKE_CROSSCOMPILING TRUE)
else()
    set(CMAKE_CROSSCOMPILING FALSE)
endif()

message(STATUS "Cross Compiling: ${CMAKE_CROSSCOMPILING}")

# 设置 C 语言标准
if(DEFINED TC_C_STANDARD AND NOT TC_C_STANDARD STREQUAL "")
    set(CMAKE_C_STANDARD ${TC_C_STANDARD})
    message(STATUS "C Language Standard: ${CMAKE_C_STANDARD}")
endif()

# 设置 C++ 语言标准
if(DEFINED TC_CXX_STANDARD AND NOT TC_CXX_STANDARD STREQUAL "")
    set(CMAKE_CXX_STANDARD ${TC_CXX_STANDARD})
    message(STATUS "C++ Language Standard: ${CMAKE_CXX_STANDARD}")
endif()

# 设置编译器
if(DEFINED TC_C_CXX_COMPILER AND NOT TC_C_CXX_COMPILER STREQUAL "")
    find_program(C_COMPILER_PATH "${TC_C_CXX_COMPILER}-gcc")
    set(CMAKE_C_COMPILER   "${C_COMPILER_PATH}"   CACHE FILEPATH "C compiler" FORCE)
    find_program(CXX_COMPILER_PATH "${TC_C_CXX_COMPILER}-g++")
    set(CMAKE_CXX_COMPILER "${CXX_COMPILER_PATH}" CACHE FILEPATH "C++ compiler" FORCE)
    message(STATUS "Compiler: ${TC_C_CXX_COMPILER}-gcc/${TC_C_CXX_COMPILER}-g++")
endif()

# 设置编译参数
if(DEFINED TC_COMPILE_OPTIONS AND NOT TC_COMPILE_OPTIONS STREQUAL "")
    # 将以空格分隔的字符串转成 CMake 列表
    string(REPLACE " " ";" TC_COMPILE_OPTIONS_LIST "${TC_COMPILE_OPTIONS}")

    # 添加编译参数，作用于所有语言（C 和 C++）
    add_compile_options(${TC_COMPILE_OPTIONS_LIST})

    message(STATUS "Added compile options: ${TC_COMPILE_OPTIONS}")
endif()

# 设置链接参数
if(DEFINED TC_LINK_OPTIONS AND NOT TC_LINK_OPTIONS STREQUAL "")
    # 将以空格分隔的字符串转换为 CMake 列表
    string(REPLACE " " ";" TC_LINK_OPTIONS_LIST "${TC_LINK_OPTIONS}")

    # 添加链接器参数，适用于所有目标
    add_link_options(${TC_LINK_OPTIONS_LIST})

    message(STATUS "Added link options: ${TC_LINK_OPTIONS}")
endif()

# 添加链接文件
if(DEFINED TC_LINK_FILE AND NOT TC_LINK_FILE STREQUAL "")
    add_link_options("-T${CMAKE_CURRENT_SOURCE_DIR}/${TC_LINK_FILE}")
    message(STATUS "Using custom linker script: ${TC_LINK_FILE}")
endif()

message(STATUS "***************************** TOOLCHAIN END *****************************")