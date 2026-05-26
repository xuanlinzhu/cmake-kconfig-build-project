# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2025-6-28
# Version: 2.0.0
# 新增移除特定C文件
# Description: 这个文件用于创建cmake的快速模板工程

# 设置需要匹配的源文件类型
set(ALL_SOURCES_TYPES "*.c" "*.cpp" "*.cxx" "*.cc" "*.S" "*.s")
# 设置需要匹配的头文件类型
set(ALL_HEADER_TYPES "*.h" "*.hpp" "*.hxx" "*.hh")
# 设置需要匹配的静态库类型
set(ALL_LIBRARY_TYPES "*.a")
# 全部源文件
set_property( GLOBAL APPEND PROPERTY ALL_CODE_SOURCES)
# 全部引用路径
set_property( GLOBAL APPEND PROPERTY ALL_CODE_INCLUDES)
# 全部静态库
set_property( GLOBAL APPEND PROPERTY ALL_CODE_LIBRARIES)


# 定义一个函数，用于输出当前源路径和当前构建路径
function(print_paths)
    message(STATUS "Src Path: ${CMAKE_CURRENT_SOURCE_DIR},Build Path: ${CMAKE_CURRENT_BINARY_DIR}")
endfunction()

#------------------辅助函数: 归一化路径------------------#
function(normalize_path INPUT_PATH OUTPUT_VAR)
    # 转换为 CMake 风格路径
    file(TO_CMAKE_PATH "${INPUT_PATH}" TMP_PATH)
    # 去掉末尾斜杠
    string(REGEX REPLACE "/$" "" TMP_PATH "${TMP_PATH}")
    set(${OUTPUT_VAR} "${TMP_PATH}" PARENT_SCOPE)
endfunction()

#------------------查找当前目录的源文件------------------#
function(find_current_source_file)
    file(GLOB CURRENT_CODE_SOURCES ${ALL_SOURCES_TYPES})
    # 如果当前路径下存在源文件，则将其添加到顶层目录的变量中
    if(CURRENT_CODE_SOURCES)
        message(STATUS "Add Source:${CURRENT_CODE_SOURCES}")
        # 将当前获取的文件传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_SOURCES ${CURRENT_CODE_SOURCES}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${CURRENT_CODE_SOURCES} PARENT_SCOPE)
    endif()
endfunction()

#------------------查找当前目录下的源文件------------------#
function(find_recurse_source_file )
    file(GLOB_RECURSE CURRENT_CODE_SOURCES ${ALL_SOURCES_TYPES})
    # 如果当前路径下存在源文件，则将其添加到顶层目录的变量中
    if(CURRENT_CODE_SOURCES)
        message(STATUS "Add Source:${CURRENT_CODE_SOURCES}")
        # 将当前获取的文件传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_SOURCES ${CURRENT_CODE_SOURCES}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${CURRENT_CODE_SOURCES} PARENT_SCOPE)
    endif()
endfunction()

#------------------添加源文件------------------#
function(add_some_source_file)
    set(ADD_FILES "")
    foreach(F_NAME ${ARGN})
        if(F_NAME)
            if(IS_ABSOLUTE "${F_NAME}")
                set(ABS_FILE "${F_NAME}")
            else()
                set(ABS_FILE "${CMAKE_CURRENT_SOURCE_DIR}/${F_NAME}")
            endif()
            normalize_path("${ABS_FILE}" ABS_FILE)
            list(APPEND ADD_FILES "${ABS_FILE}")
        endif()
    endforeach()
    if(ADD_FILES)
        message(STATUS "Add Source:${ADD_FILES}")
        set_property(GLOBAL APPEND PROPERTY ALL_CODE_SOURCES ${ADD_FILES})
    endif()
endfunction()

#------------------移除源文件------------------#
function(remove_some_source_file)
    get_property(ALL_FILES GLOBAL PROPERTY ALL_CODE_SOURCES)
    if(NOT ALL_FILES)
        message(STATUS "No source files to remove")
        return()
    endif()

    foreach(F_NAME ${ARGN})
        if(F_NAME)
            if(IS_ABSOLUTE "${F_NAME}")
                set(REMOVE_FILE "${F_NAME}")
            else()
                set(REMOVE_FILE "${CMAKE_CURRENT_SOURCE_DIR}/${F_NAME}")
            endif()
            normalize_path("${REMOVE_FILE}" REMOVE_FILE)

            # 归一化全局列表
            set(NORMALIZED_LIST "")
            foreach(P ${ALL_FILES})
                normalize_path("${P}" NP)
                list(APPEND NORMALIZED_LIST "${NP}")
            endforeach()

            list(FIND NORMALIZED_LIST "${REMOVE_FILE}" INDEX)
            if(NOT INDEX EQUAL -1)
                list(REMOVE_AT ALL_FILES ${INDEX})
                message(STATUS "Remove Source: ${REMOVE_FILE}")
            else()
                message(WARNING "Source ${REMOVE_FILE} no in ALL_CODE_SOURCES")
            endif()
        endif()
    endforeach()

    set_property(GLOBAL PROPERTY ALL_CODE_SOURCES "${ALL_FILES}")
endfunction()

#------------------加入当前目录的引用路径------------------#
function(find_current_header_dir )
    file(GLOB CURRENT_HEADER_FILES ${ALL_HEADER_TYPES})
    # 如果当前路径下存在 .h 文件，则将当前路径加入引用路径
    if(CURRENT_HEADER_FILES)
        message(STATUS "Add Include:${CMAKE_CURRENT_SOURCE_DIR}")
        # 将当前获取的引用路径传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_INCLUDES ${CMAKE_CURRENT_SOURCE_DIR}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${CMAKE_CURRENT_SOURCE_DIR} PARENT_SCOPE)
    endif()
endfunction()

#------------------加入当前目录下的引用路径------------------#
function(find_recurse_header_dir )
    file(GLOB_RECURSE CURRENT_HEADER_FILES ${ALL_HEADER_TYPES})
    set(INC_PATHS "")
    set(ABSOLUTE_PATH "")
    # 如果当前路径下存在 .h 文件，则将当前路径加入引用路径
    if(CURRENT_HEADER_FILES)
        # 遍历当前源文件的路径
        foreach(CUR_FILE ${CURRENT_HEADER_FILES})
            get_filename_component(ABSOLUTE_PATH "${CUR_FILE}" DIRECTORY)
            # 搜索 ABSOLUTE_PATH 在 INC_PATHS 中的位置
            list(FIND INC_PATHS "${ABSOLUTE_PATH}" INDEX)
            # 判断是否找到了 ABSOLUTE_PATH
            if(INDEX EQUAL -1)
                # 添加 ABSOLUTE_PATH 到 INC_PATHS 中
                list(APPEND INC_PATHS ${ABSOLUTE_PATH})
            endif()
        endforeach()
        message(STATUS "Add Include:${INC_PATHS}")
        # 将当前获取的引用路径传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_INCLUDES ${INC_PATHS}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${INC_PATHS} PARENT_SCOPE)
    endif()
endfunction()

#------------------添加引用路径------------------#
function(add_some_header_dir)
    set(ADD_PATHS "")
    foreach(D_NAME ${ARGN})
        if(D_NAME)
            if(IS_ABSOLUTE "${D_NAME}")
                set(ABS_PATH "${D_NAME}")
            else()
                set(ABS_PATH "${CMAKE_CURRENT_SOURCE_DIR}/${D_NAME}")
            endif()
            normalize_path("${ABS_PATH}" ABS_PATH)
            list(APPEND ADD_PATHS "${ABS_PATH}")
        endif()
    endforeach()
    if(ADD_PATHS)
        message(STATUS "Add Include:${ADD_PATHS}")
        set_property(GLOBAL APPEND PROPERTY ALL_CODE_INCLUDES ${ADD_PATHS})
    endif()
endfunction()

#------------------移除引用路径------------------#
function(remove_some_header_dir)
    get_property(ALL_PATHS GLOBAL PROPERTY ALL_CODE_INCLUDES)
    if(NOT ALL_PATHS)
        message(STATUS "No include paths to remove")
        return()
    endif()

    foreach(D_NAME ${ARGN})
        if(D_NAME)
            if(IS_ABSOLUTE "${D_NAME}")
                set(REMOVE_PATH "${D_NAME}")
            else()
                set(REMOVE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/${D_NAME}")
            endif()
            normalize_path("${REMOVE_PATH}" REMOVE_PATH)

            set(NORMALIZED_LIST "")
            foreach(P ${ALL_PATHS})
                normalize_path("${P}" NP)
                list(APPEND NORMALIZED_LIST "${NP}")
            endforeach()

            list(FIND NORMALIZED_LIST "${REMOVE_PATH}" INDEX)
            if(NOT INDEX EQUAL -1)
                list(REMOVE_AT ALL_PATHS ${INDEX})
                message(STATUS "Remove Include: ${REMOVE_PATH}")
            else()
                message(WARNING "Include Path ${REMOVE_PATH} no in ALL_CODE_INCLUDES")
            endif()
        endif()
    endforeach()

    set_property(GLOBAL PROPERTY ALL_CODE_INCLUDES "${ALL_PATHS}")
endfunction()

#------------------加入当前目录的静态库------------------#
function(find_current_library_file )
    file(GLOB CURRENT_CODE_LIBRARIES ${ALL_LIBRARY_TYPES})
    # 如果当前路径下存在静态库，则将其添加到顶层目录的变量中
    if(CURRENT_CODE_LIBRARIES)
        message(STATUS "添加静态库:${CURRENT_CODE_LIBRARIES}")
        # 将当前获取的静态库传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_LIBRARIES ${CURRENT_CODE_LIBRARIES}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${CURRENT_CODE_LIBRARIES} PARENT_SCOPE)
    endif()
endfunction()

#------------------加入当前目录下的静态库------------------#
function(find_recurse_library_file )

    file(GLOB_RECURSE CURRENT_CODE_LIBRARIES ${ALL_LIBRARY_TYPES})
    # 如果当前路径下存在静态库，则将其添加到顶层目录的变量中
    if(CURRENT_CODE_LIBRARIES)
        message(STATUS "Add Lib:${CURRENT_CODE_LIBRARIES}")
        # 将当前获取的静态库传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_LIBRARIES ${CURRENT_CODE_LIBRARIES}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${CURRENT_CODE_LIBRARIES} PARENT_SCOPE)
    endif()
endfunction()

#------------------添加静态库------------------#
function(add_some_library_file)
    set(ADD_LIBS "")
    foreach(L_NAME ${ARGN})
        if(L_NAME)
            if(IS_ABSOLUTE "${L_NAME}")
                set(ABS_LIB "${L_NAME}")
            else()
                set(ABS_LIB "${CMAKE_CURRENT_SOURCE_DIR}/${L_NAME}")
            endif()
            normalize_path("${ABS_LIB}" ABS_LIB)
            list(APPEND ADD_LIBS "${ABS_LIB}")
        endif()
    endforeach()
    if(ADD_LIBS)
        message(STATUS "Add Lib:${ADD_LIBS}")
        set_property(GLOBAL APPEND PROPERTY ALL_CODE_LIBRARIES ${ADD_LIBS})
    endif()
endfunction()

#------------------移除静态库------------------#
function(remove_some_library_file)
    get_property(ALL_LIBS GLOBAL PROPERTY ALL_CODE_LIBRARIES)
    if(NOT ALL_LIBS)
        message(STATUS "No libraries to remove")
        return()
    endif()

    foreach(L_NAME ${ARGN})
        if(L_NAME)
            if(IS_ABSOLUTE "${L_NAME}")
                set(REMOVE_LIB "${L_NAME}")
            else()
                set(REMOVE_LIB "${CMAKE_CURRENT_SOURCE_DIR}/${L_NAME}")
            endif()
            normalize_path("${REMOVE_LIB}" REMOVE_LIB)

            set(NORMALIZED_LIST "")
            foreach(P ${ALL_LIBS})
                normalize_path("${P}" NP)
                list(APPEND NORMALIZED_LIST "${NP}")
            endforeach()

            list(FIND NORMALIZED_LIST "${REMOVE_LIB}" INDEX)
            if(NOT INDEX EQUAL -1)
                list(REMOVE_AT ALL_LIBS ${INDEX})
                message(STATUS "Remove Lib: ${REMOVE_LIB}")
            else()
                message(WARNING "Lib ${REMOVE_LIB} no in ALL_CODE_LIBRARIES")
            endif()
        endif()
    endforeach()

    set_property(GLOBAL PROPERTY ALL_CODE_LIBRARIES "${ALL_LIBS}")
endfunction()

#------------------添加项目源码的顶层构建文件------------------#
function(set_external_path PATH BINARY_NAME)
    # 添加外部路径
    set(EXTERNAL_SOURCE_DIR "${PATH}")
    message(STATUS "Add extra path: ${EXTERNAL_SOURCE_DIR} as ${BINARY_NAME}")
    # 添加外部路径，并指定与之对应的二进制目录
    add_subdirectory(${EXTERNAL_SOURCE_DIR} ${BINARY_NAME})
endfunction()

#------------------查找当前目录下一级的所有构建文件------------------#
function(find_cmakelists_current_dir )
    # 将传递给函数的所有参数存储在 EXCLUDE_FOLDERS 变量中
    set(EXCLUDE_FOLDERS ${ARGN})
    # 查找目标路径下的所有文件夹(不递归)
    file(GLOB SUBDIR_LIST RELATIVE  ${CMAKE_CURRENT_SOURCE_DIR} */)

    # 过滤出文件夹
    foreach(SUBDIR ${SUBDIR_LIST})
        #检查是否为文件夹 
        if(IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${SUBDIR})
            # 检查当前文件夹是否在排除列表中
            list(FIND EXCLUDE_FOLDERS ${SUBDIR} EXCLUDE_INDEX)
            if(EXCLUDE_INDEX EQUAL -1)
                # 检查是否存在CMakeLists.txt文件
                if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${SUBDIR}/CMakeLists.txt)
                    message(STATUS "Traverse the path:CMakeLists.txt found in ${SUBDIR}, adding to build")
                    # 添加到构建路径
                    add_subdirectory(${SUBDIR})
                else()
                    # message(STATUS "-->CMakeLists.txt not found in ${SUBDIR}, skipping")
                endif()
            endif()
        endif()
    endforeach()    
endfunction()

# ------------------非模块的构建模板函数------------------#
function(list_template )
    set(TEMP_ARG ${ARGN})
    # 判断是否传入参数
    if(TEMP_ARG)
        # 检查该参数是否被定义
        if(DEFINED ${TEMP_ARG})
            # message(STATUS "${TEMP_ARG} is defined")
        else()
            # message(STATUS "${TEMP_ARG} is not defined")
            return()
        endif()
    endif()
    # 执行后续的代码
    print_paths()
    find_current_source_file()
    find_current_header_dir()
    find_current_library_file()
    find_cmakelists_current_dir()
endfunction()

# ------------------模块的构建模板函数------------------#
function(module_template )
    set(TEMP_ARG ${ARGN})
    # 判断是否传入参数
    if(TEMP_ARG)
        # 检查该参数是否被定义
        if(DEFINED ${TEMP_ARG})
            # message(STATUS "${TEMP_ARG} is defined")
        else()
            # message(STATUS "${TEMP_ARG} is not defined")
            return()
        endif()
    endif()
    print_paths()
    find_recurse_source_file()
    find_recurse_header_dir()
    find_recurse_library_file()
endfunction()

#------------------打印工程包含的所有源文件------------------#
function(print_all_code_sources )
    # 将传递给函数的所有参数存储
    set(ALL_SOURCES ${ARGN})
    set(SRC_LIST "")
    # 将 ALL_CODE_SOURCES 的内容保存到 SRC_LIST 中
    get_property(SRC_LIST GLOBAL PROPERTY ALL_CODE_SOURCES )
    # 打印所有的源文件
    message(STATUS "All Source:${SRC_LIST}")
    if(ALL_SOURCES)
        # 将 SRC_LIST 的值设置给 ALL_SOURCES
        set(${ALL_SOURCES} ${SRC_LIST} PARENT_SCOPE)
    endif()

endfunction()

#------------------打印工程包含的所有引用路径------------------#
function(print_all_code_includes)
    # 将传递给函数的所有参数存储
    set(ALL_INCLUDES ${ARGN})
    set(INC_LIST "")
    # 将 ALL_CODE_INCLUDES 的内容保存到 INC_LIST 中
    get_property(INC_LIST GLOBAL PROPERTY ALL_CODE_INCLUDES )
    # 打印所有的引用路径
    message(STATUS "All Include:${INC_LIST}")
    if(ALL_INCLUDES)
        # 将 SRC_LIST 的值设置给 ALL_SOURCES
        set(${ALL_INCLUDES} ${INC_LIST} PARENT_SCOPE)
    endif()
endfunction()

#------------------打印工程包含的所有静态库------------------#
function(print_all_code_librarys)
    # 将传递给函数的所有参数存储
    set(ALL_LIBRARYS ${ARGN})
    set(LIB_LIST "")
    # 将 ALL_CODE_INCLUDES 的内容保存到 INC_LIST 中
    get_property(LIB_LIST GLOBAL PROPERTY ALL_CODE_LIBRARIES )
    # 打印所有的引用路径
    message(STATUS "All libs:${LIB_LIST}")
    if(ALL_LIBRARYS)
        # 将 SRC_LIST 的值设置给 ALL_SOURCES
        set(${ALL_LIBRARYS} ${LIB_LIST} PARENT_SCOPE)
    endif()
endfunction()

#------------------Add external module paths by scanning Kconfig------------------#
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
