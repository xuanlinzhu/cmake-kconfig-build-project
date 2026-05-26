# CMake 公共函数说明

## 1. 文件分工

CK Build 的 CMake 公共能力主要分在三个文件中：

```text
ck_tools/ck_utils.cmake
ck_tools/ck_toolchain.cmake
ck_tools/ck_project.cmake
```

| 文件 | 职责 |
| --- | --- |
| `ck_utils.cmake` | 底层扫描函数：源码、头文件、库、子 CMake 目录 |
| `ck_toolchain.cmake` | 将 Kconfig 工具链配置导入 CMake |
| `ck_project.cmake` | 工程级流程函数：profile、target、输出目录、产物生成等 |

一般用户主要改项目自己的 `CMakeLists.txt`，不需要频繁修改这些公共文件。

## 2. Profile 函数

Profile 用来设置某类工程的默认行为。

### 2.1 `ck_profile_generic()`

通用工程默认配置。

特点：

- 不设置目标后缀。
- 默认不生成 bin / dis / size。
- 默认排除 `build`、`bin`。
- 链接模式为 scoped，也就是默认 `PRIVATE`。

适合：

- 普通 C/C++ 应用。
- Linux / Windows / macOS 本机程序。
- 单元测试程序。

### 2.2 `ck_profile_mcu()`

通用 MCU 工程默认配置。

特点：

- 目标后缀为 `.elf`。
- 默认生成 map / bin / dis / size。
- 链接模式为 scoped。

适合：

- GD32 / CH32 / NXP / 裸机 ARM 等非 CubeMX 工程。

### 2.3 `ck_profile_stm32()`

STM32CubeMX 工程默认配置。

特点：

- 目标后缀为 `.elf`。
- 默认生成 map / bin / dis / size。
- 链接模式为 plain，兼容 CubeMX 子工程。
- 默认排除 `build`、`bin`、`cmake`、`Core`、`Drivers`。

适合：

- STM32CubeMX 生成的 CMake 工程。

### 2.4 `ck_profile_linux_app()`

Linux 应用工程默认配置。

特点：

- 不设置目标后缀。
- 默认不生成 bin / dis / size。
- 链接模式为 scoped。

适合：

- Linux C / C++ 应用。
- 需要保留 Linux 平台默认输出行为的工程。

## 3. 工程开始与默认配置

### 3.1 `ck_project_begin(target)`

打印工程开始信息，并在存在 `print_paths()` 时打印路径信息。

推荐放在 `project()` 之后：

```cmake
project(${PRO_NAME} LANGUAGES C CXX ASM)
ck_project_begin(${PRO_NAME})
```

### 3.2 `ck_project_set_defaults()`

对 profile 设置进行兜底和归一化。

它会处理：

- `CK_PROJECT_TYPE`
- `CK_LINK_LIBRARIES_MODE`
- `CK_TARGET_SUFFIX`
- `CK_EXCLUDE_DIRS`
- `TC_GENERATE_MAP_FILE`
- `TC_PRINT_MEMORY_USAGE`
- `TC_GENERATE_BIN`
- `TC_GENERATE_DISASSEMBLY`
- `TC_PRINT_SIZE`

推荐在 profile 后调用：

```cmake
ck_profile_generic()
ck_project_set_defaults()
```

### 3.3 `ck_project_end(target)`

打印工程配置结束信息。

推荐放在 CMakeLists 末尾：

```cmake
ck_project_end(${PRO_NAME})
```

## 4. 输出目录与目标

### 4.1 `ck_set_output_dirs()`

设置可执行文件、动态库、静态库输出目录。

常用写法：

```cmake
ck_set_output_dirs(OUTPUT_DIR "${CMAKE_BINARY_DIR}/../bin")
```

效果：

```cmake
CMAKE_RUNTIME_OUTPUT_DIRECTORY
CMAKE_LIBRARY_OUTPUT_DIRECTORY
CMAKE_ARCHIVE_OUTPUT_DIRECTORY
```

都指向统一输出目录。

### 4.2 `ck_create_target(target)`

创建可执行目标。

```cmake
ck_create_target(${PRO_NAME})
```

如果 profile 设置了 `CK_TARGET_SUFFIX`，会自动设置目标后缀。

STM32 工程中通常会得到：

```text
ck_project.elf
```

## 5. 工程扫描函数

### 5.1 `ck_collect_current_sources()`

扫描当前工程目录下的源码文件。

依赖底层函数：

```cmake
find_recurse_source_file()
```

通常会收集：

```text
.c
.cpp
.cc
.cxx
.s
.S
.asm
```

是否递归、排除哪些目录，由底层扫描函数和 `CK_EXCLUDE_DIRS` 控制。

### 5.2 `ck_collect_current_includes()`

扫描当前工程目录下的头文件路径。

依赖底层函数：

```cmake
find_recurse_header_dir()
```

### 5.3 `ck_collect_kconfig_external_paths()`

从工程 Kconfig 的外部模块区解析外部模块路径。

```cmake
ck_collect_kconfig_external_paths(KCONFIG_FILE "${CMAKE_CURRENT_SOURCE_DIR}/Kconfig")
```

它会扫描：

```kconfig
# CK_TOOL_EXTERNAL_START
source "$(CK_WORKSPACE_ROOT)/package/Kconfig"
# CK_TOOL_EXTERNAL_END
```

并把对应路径加入构建搜索。

### 5.4 `ck_collect_cmake_subdirs()`

扫描当前目录下一层带 `CMakeLists.txt` 的子目录，并添加到构建。

适合：

- `app/`
- `module/`
- `test/`

不适合：

- 深层复杂第三方库。
- 不希望自动加入的目录。

这些目录应加入 `CK_EXCLUDE_DIRS`。

### 5.5 `ck_collect_print_project_files()`

打印当前收集到的：

- 源文件。
- 头文件路径。
- 库文件。

用于调试扫描结果。

### 5.6 `ck_normalize_project_files()`

对扫描结果去重，避免同一源码、头文件目录、库文件重复加入。

建议在所有扫描函数之后调用。

## 6. 应用到 target

### 6.1 `ck_target_apply_sources(target)`

把 `SRC_FILES` 加入目标：

```cmake
ck_target_apply_sources(${PRO_NAME})
```

等价于封装后的：

```cmake
target_sources(${PRO_NAME} PRIVATE ${SRC_FILES})
```

### 6.2 `ck_target_apply_includes(target)`

把 `INCLUDE_PATH` 加入目标：

```cmake
ck_target_apply_includes(${PRO_NAME})
```

等价于封装后的：

```cmake
target_include_directories(${PRO_NAME} PRIVATE ${INCLUDE_PATH})
```

### 6.3 `ck_target_apply_library_dirs(target)`

把 Kconfig 工具链配置中的 `TC_LIBRARY_DIRS` 加入目标库搜索路径。

### 6.4 `ck_target_apply_definitions(target)`

把 Kconfig 工具链配置中的 `TC_DEFINE_MACROS` 加入目标宏定义。

### 6.5 `ck_target_apply_toolchain_libraries(target)`

把 Kconfig 工具链配置中的 `TC_LINK_LIBRARIES` 链接到目标。

### 6.6 `ck_target_apply_project_libraries(target)`

把扫描到或手动追加的 `LIB_FILES` 链接到目标。

## 7. 链接模式

公共函数提供：

```cmake
ck_target_link_libraries(target ...)
```

默认使用：

```cmake
target_link_libraries(target PRIVATE ...)
```

如果：

```cmake
set(CK_LINK_LIBRARIES_MODE plain)
```

则使用 plain signature：

```cmake
target_link_libraries(target ...)
```

STM32CubeMX 工程使用 plain 模式，是为了兼容 CubeMX 生成的子工程写法。

## 8. Binutils 工具查找

### 8.1 `ck_find_binutils_tool()`

用于查找：

- `objcopy`
- `objdump`
- `size`

通用工程：

```cmake
ck_find_binutils_tool(CMAKE_OBJCOPY
    TOOL_NAME objcopy
)
```

STM32 工程：

```cmake
ck_find_binutils_tool(CMAKE_OBJCOPY
    TOOL_NAME objcopy
    NAMES arm-none-eabi-objcopy
    FALLBACK_NAME "bin"
)
```

查找顺序：

1. 如果工具链文件已经设置 `CMAKE_OBJCOPY` 等变量，直接使用。
2. 根据 `CMAKE_C_COMPILER` 推导工具链前缀，比如 `arm-none-eabi-gcc` 推导出 `arm-none-eabi-objcopy`。
3. 在编译器同目录查找。
4. 在 PATH 中查找。

### 8.2 `ck_print_binutils_tools()`

打印当前找到的工具路径：

```cmake
ck_print_binutils_tools()
```

## 9. 构建产物生成

### 9.1 `ck_target_enable_map(target)`

如果 `TC_GENERATE_MAP_FILE` 开启，则添加 map 文件链接参数。

GNU / Clang 下会添加：

```text
-Wl,-Map=xxx.map
-Wl,--cref
```

如果 `TC_PRINT_MEMORY_USAGE` 开启，还会添加：

```text
-Wl,--print-memory-usage
```

### 9.2 `ck_target_generate_bin(target)`

如果 `TC_GENERATE_BIN` 开启，并且找到 `CMAKE_OBJCOPY`，则生成：

```text
bin/<target>.bin
```

### 9.3 `ck_target_generate_disassembly(target)`

如果 `TC_GENERATE_DISASSEMBLY` 开启，并且找到 `CMAKE_OBJDUMP`，则生成：

```text
bin/<target>.dis
```

### 9.4 `ck_target_generate_size(target)`

如果 `TC_PRINT_SIZE` 开启，并且找到 `CMAKE_SIZE`，则：

- 在终端打印 Berkeley 格式 size。
- 保存完整段信息到：

```text
bin/<target>.size.txt
```

## 10. 单元测试

### `ck_target_enable_test(target)`

如果 `CK_TEST_UNIT` 开启：

```cmake
enable_testing()
add_test(NAME ${target}_unit COMMAND $<TARGET_FILE:${target}>)
```

执行测试：

```bash
ctest --test-dir build
```

## 11. 常用变量表

| 变量 | 来源 | 说明 |
| --- | --- | --- |
| `PRO_NAME` | Kconfig -> ck_config.cmake | 工程目标名 |
| `CK_TOOLS_ROOT` | Kconfig -> ck_config.cmake | ck_tools 路径 |
| `CK_WORKSPACE_ROOT` | Kconfig -> ck_config.cmake | 工作区路径 |
| `CK_EXCLUDE_DIRS` | profile / 用户配置区 | 扫描排除目录 |
| `SRC_FILES` | 扫描函数 / 手动追加 | 源文件列表 |
| `INCLUDE_PATH` | 扫描函数 / 手动追加 | 头文件路径列表 |
| `LIB_FILES` | 扫描函数 / 手动追加 | 库文件列表 |
| `TC_DEFINE_MACROS` | Kconfig.toolchain | 编译宏 |
| `TC_LIBRARY_DIRS` | Kconfig.toolchain | 库搜索路径 |
| `TC_LINK_LIBRARIES` | Kconfig.toolchain | 链接库 |
| `TC_GENERATE_BIN` | profile / Kconfig.toolchain | 是否生成 bin |
| `TC_GENERATE_DISASSEMBLY` | profile / Kconfig.toolchain | 是否生成 dis |
| `TC_GENERATE_MAP_FILE` | profile / Kconfig.toolchain | 是否生成 map |
| `TC_PRINT_SIZE` | profile | 是否打印并保存 size |

## 12. 修改公共函数的建议

优先级建议：

1. 能在项目 `CMakeLists.txt` 用户配置区解决的，不改公共函数。
2. 只有某个平台需要的逻辑，放平台模板的扩展区或链接修正区。
3. 多个模板重复出现的逻辑，再沉淀到 `ck_project.cmake`。
4. 底层扫描规则变化，才修改 `ck_utils.cmake`。
5. 工具链 Kconfig 配置变化，才修改 `ck_toolchain.cmake` 和 `Kconfig.toolchain`。

这样可以避免公共层越来越重。
