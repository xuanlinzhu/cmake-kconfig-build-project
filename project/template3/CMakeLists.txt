cmake_minimum_required(VERSION 3.1)
include(../../tools/ck_cmlib.cmake)

SET(CMAKE_C_COMPILER_WORKS TRUE)
SET(CMAKE_CXX_COMPILER_WORKS FAULT)


set(CROSS_COMPILE "arm-xilinx-linux-gnueabi" )

add_compile_options(-mthumb -mfpu=neon -mfloat-abi=hard -mcpu=cortex-a9 --sysroot=/opt/petalinux/2020.2/sysroots/cortexa9t2hf-neon-xilinx-linux-gnueabi)
# add_link_options(-mthumb -mfpu=neon -mfloat-abi=hard -mcpu=cortex-a9 --sysroot=/opt/petalinux/2020.2/sysroots/cortexa9t2hf-neon-xilinx-linux-gnueabi)
# add_link_options(-T${CMAKE_CURRENT_SOURCE_DIR}/link.lds)
# add_link_options(-Wl,-Map=${CMAKE_CURRENT_SOURCE_DIR}/bin/${PRO_NAME}.map,-cref)
add_link_options("-Wl,--dynamic-linker=/lib/ld-linux-armhf.so.3")

#告诉cmake是进行交叉编译
SET(CMAKE_CROSSCOMPILING TRUE)

SET(CMAKE_SYSTEM_NAME Generic)

SET(CMAKE_C_COMPILER "${CROSS_COMPILE}-gcc")
SET(CMAKE_CXX_COMPILER "${CROSS_COMPILE}-g++")

SET(CMAKE_SYSTEM_PROCESSOR "arm")

project(${PRO_NAME})

message("---------------开始构建----------------")
print_paths()

set(OUTPUT_DIR "../bin")
# 控制生成的可执行文件（例如：.exe 文件）的输出目录。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${OUTPUT_DIR})
#控制生成的共享库（例如：.dll 文件）的输出目录
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${OUTPUT_DIR})
#控制生成的静态库（例如：.lib 文件）的输出目录。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${OUTPUT_DIR})
#设置工程名字

# 寻找当前文件夹的源文件
find_current_source_file()
find_current_header_dir()

# 配置外部工程路径
set_external_path("${ROOT_PATH}/source" "source")
# 排除搜索路径
find_cmakelists_current_dir("build" "bin")

print_all_code_sources(SRC_FILES)
set_source_files_properties(${SRC_FILES} PROPERTIES LANGUAGE C)
print_all_code_includes(INCLUDE_PATH)
print_all_code_librarys(LIB_FILES)

INCLUDE_DIRECTORIES(${INCLUDE_PATH})

add_executable(${PRO_NAME} ${SRC_FILES})

# #make bin命令即可生成bin文件
# ADD_CUSTOM_COMMAND(TARGET ${PRO_NAME} POST_BUILD COMMAND ${CROSS_COMPILE}-objcopy -O binary ${PROJECT_SOURCE_DIR}/bin/${PRO_NAME} ${PROJECT_SOURCE_DIR}/bin/${PRO_NAME}.bin)

# #make bin命令即可生成反汇编文件
# ADD_CUSTOM_COMMAND(TARGET ${PRO_NAME} POST_BUILD COMMAND ${CROSS_COMPILE}-objdump -D ${PROJECT_SOURCE_DIR}/bin/${PRO_NAME} > ${PROJECT_SOURCE_DIR}/bin/${PRO_NAME}.dis)

# if(NOT ${LIB_FILES})
# 	target_link_libraries(${PRO_NAME} ${LIB_FILES})
# endif()




