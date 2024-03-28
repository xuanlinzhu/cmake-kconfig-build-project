@echo off
REM Author: zhuxuanlin
REM Email: xuanlinzhu@qq.com
REM Date: 2024-3-26
REM Version: 1.0
REM
REM Description: 这个文件用于工程配置、构建、编译、清除的指令集合文件

REM Check if one parameter is passed
if "%~1"=="" (
    echo Please input one parameter [ build make clean config auto help ].
    exit /b
)

REM Process the passed parameter
set "param=%~1"
if /i "%param%"=="auto" goto :config_func
if /i "%param%"=="config" goto :config_func
if /i "%param%"=="build" goto :build_func
if /i "%param%"=="make" goto :make_func
if /i "%param%"=="clean" goto :clean_func
if /i "%param%"=="help" goto :help_func

REM Convert shorthand parameters to full parameters if necessary
if /i "%param%"=="a" set "param=auto" & goto :config_func
if /i "%param%"=="cn" set "param=config" & goto :config_func
if /i "%param%"=="b" set "param=build" & goto :build_func
if /i "%param%"=="m" set "param=make" & goto :make_func
if /i "%param%"=="cl" set "param=clean" & goto :clean_func
if /i "%param%"=="h" set "param=help" & goto :help_func

echo Invalid parameter: %~1, please input build make clean config auto help.
exit /b

REM -------------------config----------------------
:config_func
echo Executing config operation...
REM Add your config command here
menuconfig
echo Executing ck_pylib.py .
python ck_pylib.py
REM by auto
if /i "%param%"=="auto" goto :build_func
goto :end

REM -------------------build----------------------
:build_func
echo Executing build operation...
REM Add your build command here
REM Check if the "build" folder exists in the current directory
if exist build (
    echo Deleting existing build directory...
    rmdir /s /q build
)

REM Create the "build" folder
echo Creating build directory...
mkdir build

REM Enter the "build" folder
cd build

REM Run the CMake command in the "build" folder
echo Running CMake...
cmake -G "MinGW Makefiles" ../

REM Return to the parent directory
cd ..

REM by auto
if /i "%param%"=="auto" goto :make_func
goto :end

REM -------------------make----------------------
:make_func
echo Executing make operation...
REM Add your make command here

REM 进入 build 文件夹
cd build

REM 在 build 文件夹中执行 make 命令
echo Running make...
make

REM 返回上一级目录
cd ..

goto :end

REM -------------------clean----------------------
:clean_func
echo Executing clean operation...
REM Add your clean command here

REM 进入 build 文件夹
cd build

REM 在 build 文件夹中执行 make clean 命令
echo Running make clean...
make clean

REM 返回上一级目录
cd ..

goto :end


REM -------------------help----------------------
:help_func
echo Displays help information...
echo Usage: ck_script [ build make clean config auto help ]
echo - auto     (a) : Perform auto operation.
echo - config   (cn): Perform config operation.
echo - build    (b) : Perform build operation.
echo - make     (m) : Perform make operation.
echo - clean    (cl): Perform clean operation.
echo - help     (h) : Display this help message.
goto :end

:end
echo ck_script processed.
