## 目录说明

以下是对当前目录下文件和文件夹的详细说明：

| **路径** | **描述** |
|----------|----------|
| `script` | 构建相关的核心脚本文件 |
| `kconfiglib`| 构建所需的python库文件 |

## CK构建的环境配置

## 🖥️ Windows 下配置

### 步骤 1：安装 Python
前往 Python 官网 下载并安装的 `python-3.11.9-amd64.exe`，并确保勾选 Add to PATH。建议是3.11.9版本，因为后续使用的`windows_curses-2.3.2-cp311-cp311-win_amd64.whl`依赖的python版本是3.11.9,新版的python版本可能无法正常使用该库。

`tools/ware`目录下有python安装包

验证安装 输入`python --version`命令，如果返回版本信息，则说明 python 安装成功。


### 步骤 2：安装 CMake


前往 CMake 官网 下载 Windows 安装包（推荐使用 .msi 安装程序），并在安装时选择“添加到系统路径”。


验证安装：输入`cmake --version` 命令，如果返回版本信息，则说明 CMake 安装成功。

### 步骤 3：安装 Kconfiglib
使用 pip 安装：

`pip install kconfiglib`安装Kconfiglib，也可以使用`tools/ware`目录下的kconfiglib离线安装。

`python -m kconfiglib --version`验证是否安装成功。

### 步骤 4：安装 Kconfiglib

windows下由于 menuconfig.py 使用了 curses 库来生成文本用户界面，你需要单独安装 windows-curses


`pip install windows-curses` 建议安装`tools/ware`目录下的windows-curses 离线包。



## 🐧 Linux 下配置（以 Ubuntu/Debian 为例）
### 步骤 1：安装 Python
大多数 Linux 发行版默认已安装 Python。如果没有，请执行以下命令来安装：


`sudo apt update`


`sudo apt install python3 python3-pip`


### 步骤 2：安装 CMake
使用包管理器安装 CMake：

`sudo apt install cmake`

### 步骤 3：安装 Kconfiglib

使用 pip 安装 Kconfiglib：

`pip3 install kconfiglib`

### 步骤 4：安装 ncurses 库
由于 menuconfig.py 需要使用 curses 来提供文本用户界面，在 Linux 上你需要确保系统已经安装了 ncurses 库。可以使用以下命令进行安装：

`sudo apt install libncurses5-dev libncursesw5-dev`

### 步骤 5：安装 thinker 库


`sudo apt install python3-tk`