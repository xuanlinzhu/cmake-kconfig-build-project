#!/bin/bash
# Author: zhuxuanlin
# Email: xuanlinzhu@qq.com
# Date: 2024-3-26
# Version: 1.0
#
# Description: 这个文件用于工程配置、构建、编译、清除的指令集合文件

# Config function
config_func() {
    echo "Executing config operation..."
    # Add your config command here
    #如果是直接git下载Kconfiglib的源码，加入环境变量使用这个menuconfig.py指令
    menuconfig.py
    #如果是通过pip安装的Kconfig，使用menuconfig指令
    # menuconfig
    echo "Executing ck_pylib.py ."
    python3 ./ck_pylib.py
    # by auto
    if [ "${param,,}" = "auto" ] || [ "${param,,}" = "a" ]; then
        build_func
    fi
}

# Build function
build_func() {
    echo "Executing build operation..."
    # Add your build command here
    # Check if the "build" folder exists in the current directory
    if [ -d "build" ]; then
        echo "Deleting existing build directory..."
        rm -rf build
    fi
    # Create the "build" folder
    echo "Creating build directory..."
    mkdir build
    # Enter the "build" folder
    cd build || exit
    # Run the CMake command in the "build" folder
    echo "Running CMake..."
    cmake -G "Unix Makefiles" ../
    # Return to the parent directory
    cd ..
    # by auto
    if [ "${param,,}" = "auto" ] || [ "${param,,}" = "a" ]; then
        make_func
    fi
}

# Make function
make_func() {
    echo "Executing make operation..."
    # Add your make command here
    # Enter the "build" folder
    cd build 
    # Run make command in the "build" folder
    echo "Running make..."
    make
    # Return to the parent directory
    cd ..
}

# Clean function
clean_func() {
    echo "Executing clean operation..."
    # Add your clean command here
    # Enter the "build" folder
    cd build || exit
    # Run make clean command in the "build" folder
    echo "Running make clean..."
    make clean
    # Return to the parent directory
    cd ..
}

# Help function
help_func() {
    echo "Displays help information..."
    echo "Usage: $0 [ build make clean config auto help ]"
    echo "- auto     (a) : Perform auto operation."
    echo "- config   (cn): Perform config operation."
    echo "- build    (b) : Perform build operation."
    echo "- make     (m) : Perform make operation."
    echo "- clean    (cl): Perform clean operation."
    echo "- help     (h) : Display this help message."
}

# Check if one parameter is passed
if [ -z "$1" ]; then
    echo "Please input one parameter [ build make clean config auto help ]."
    exit 1
fi

# Process the passed parameter
param="$1"
if [ "${param,,}" = "auto" ] || [ "${param,,}" = "a" ]; then
    config_func
elif [ "${param,,}" = "config" ] || [ "${param,,}" = "cn" ]; then
    config_func
elif [ "${param,,}" = "build" ] || [ "${param,,}" = "b" ]; then
    build_func
elif [ "${param,,}" = "make" ] || [ "${param,,}" = "m" ]; then
    make_func
elif [ "${param,,}" = "clean" ] || [ "${param,,}" = "cl" ]; then
    clean_func
elif [ "${param,,}" = "help" ] || [ "${param,,}" = "h" ]; then
    help_func
else
    echo "Invalid parameter: $1, please input build make clean config auto help."
    exit 1
fi

echo "ck_script processed."
