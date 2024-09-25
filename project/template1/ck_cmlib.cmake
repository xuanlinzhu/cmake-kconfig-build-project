# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2024-3-26
# Version: 1.0
#
# Description: 这个文件用于创建cmake的快速模板工程

include(ck_config.cmake)

# 设置需要匹配的源文件类型
set(ALL_SOURCES_TYPES "*.c" "*.cpp" "*.S" "*.s")
# 设置需要匹配的头文件类型
set(ALL_HEADER_TYPES "*.h")
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
    message(STATUS "源路径: ${CMAKE_CURRENT_SOURCE_DIR}，构建路径: ${CMAKE_CURRENT_BINARY_DIR}")
endfunction()

#------------------查找当前目录的源文件------------------#
function(find_current_source_file)
    file(GLOB CURRENT_CODE_SOURCES ${ALL_SOURCES_TYPES})
    # 如果当前路径下存在源文件，则将其添加到顶层目录的变量中
    if(CURRENT_CODE_SOURCES)
        message(STATUS "添加源文件:${CURRENT_CODE_SOURCES}")
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
        message(STATUS "添加源文件:${CURRENT_CODE_SOURCES}")
        # 将当前获取的文件传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_SOURCES ${CURRENT_CODE_SOURCES}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${CURRENT_CODE_SOURCES} PARENT_SCOPE)
    endif()
endfunction()

#------------------添加当前目录下的特定源文件------------------#
function(add_some_source_file )
    set(ADD_FILES "")
    # 遍历所有输入参数
    foreach(F_NAME ${ARGN})
        # 判断输入函数是否为空
        if(F_NAME)
            # message(STATUS "添加特定源文件:${F_NAME}")
            list(APPEND ADD_FILES ${CMAKE_CURRENT_SOURCE_DIR}/${F_NAME})
        endif()
    endforeach()
    
    # 如果添加了源文件，则将其添加到顶层目录的变量中
    if(ADD_FILES)
        message(STATUS "添加源文件:${ADD_FILES}")
        # 将当前获取的文件传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_SOURCES ${ADD_FILES}) 
    endif()
endfunction()


#------------------从全局变量中移除特定源文件------------------#
function(remove_some_source_file )
    # 获取全局变量中的所有文件
    get_property(ALL_FILES GLOBAL PROPERTY ALL_CODE_SOURCES)
    if(NOT ALL_FILES)
        message(STATUS "没有文件可移除")
        return()
    endif()

    # 遍历所有输入参数
    foreach(F_NAME ${ARGN})
        # 判断输入文件名是否为空
        if(F_NAME)
            set(REMOVE_FILE "${CMAKE_CURRENT_SOURCE_DIR}/${F_NAME}")
            list(FIND ALL_FILES "${REMOVE_FILE}" INDEX)
            if(NOT INDEX EQUAL -1)
                list(REMOVE_AT ALL_FILES ${INDEX})
                message(STATUS "移除特定源文件: ${REMOVE_FILE}")
            else()
                message(WARNING "文件 ${REMOVE_FILE} 不存在于 ALL_CODE_SOURCES 中")
            endif()
        endif()
    endforeach()

    # 更新全局变量
    set_property(GLOBAL PROPERTY ALL_CODE_SOURCES "${ALL_FILES}")
endfunction()




#------------------加入当前目录的引用路径------------------#
function(find_current_header_dir )
    file(GLOB CURRENT_HEADER_FILES ${ALL_HEADER_TYPES})
    # 如果当前路径下存在 .h 文件，则将当前路径加入引用路径
    if(CURRENT_HEADER_FILES)
        message(STATUS "添加引用:${CMAKE_CURRENT_SOURCE_DIR}")
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
        message(STATUS "添加引用:${INC_PATHS}")
        # 将当前获取的引用路径传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_INCLUDES ${INC_PATHS}) 
    endif()
    # 将传递给函数的所有参数存储
    set(TEMP_ARG ${ARGN})
    if(TEMP_ARG)
        set(${TEMP_ARG} ${INC_PATHS} PARENT_SCOPE)
    endif()
endfunction()

#------------------添加特定的引用路径------------------#
function(add_some_header_dir )
    set(ADD_FILES "")
    # 遍历所有输入参数
    foreach(F_NAME ${ARGN})
        # 判断输入函数是否为空
        if(F_NAME)
            list(APPEND ADD_FILES ${CMAKE_CURRENT_SOURCE_DIR}/${F_NAME})
        endif()
    endforeach()
    
    # 如果添加了路径，则将其添加到顶层目录的变量中
    if(ADD_FILES)
        message(STATUS "添加引用:${ADD_FILES}")
        # 将当前获取的文件传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_INCLUDES ${ADD_FILES}) 
    endif()
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

#------------------添加当前目录下的特定源文件------------------#
function(add_some_library_file )
    set(ADD_FILES "")
    # 遍历所有输入参数
    foreach(F_NAME ${ARGN})
        # 判断输入函数是否为空
        if(F_NAME)
            list(APPEND ADD_FILES ${CMAKE_CURRENT_SOURCE_DIR}/${F_NAME})
        endif()
    endforeach()
    
    # 如果添加了源文件，则将其添加到顶层目录的变量中
    if(ADD_FILES)
        message(STATUS "添加静态库:${ADD_FILES}")
        # 将当前获取的文件传输至全局变量
        set_property( GLOBAL APPEND PROPERTY ALL_CODE_LIBRARIES ${ADD_FILES}) 
    endif()
endfunction()

#------------------添加项目源码的顶层构建文件------------------#
function(set_external_path PATH BINARY_NAME)
    # 添加外部路径
    set(EXTERNAL_SOURCE_DIR "${PATH}")
    message(STATUS "添加外部路径: ${EXTERNAL_SOURCE_DIR} as ${BINARY_NAME}")
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
                    message(STATUS "遍历路径:CMakeLists.txt found in ${SUBDIR}, adding to build")
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
    message(STATUS "所有的源文件:${SRC_LIST}")
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
    message(STATUS "所有的引用路径:${INC_LIST}")
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
    message(STATUS "所有的静态库:${LIB_LIST}")
    if(ALL_LIBRARYS)
        # 将 SRC_LIST 的值设置给 ALL_SOURCES
        set(${ALL_LIBRARYS} ${LIB_LIST} PARENT_SCOPE)
    endif()
endfunction()

