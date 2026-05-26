---
name: ck-build-helper
description: 在用户询问 CK Build 工程如何配置、构建、编译、清理、修改 Kconfig、新增 package、修改 CMakeLists 或排查常见构建错误时使用。本 Skill 适用于 xuanlinzhu/cmake-kconfig-build-project 的 ck-build-v2.0 分支，重点约束回答必须基于当前真实命令和工程结构，不编造不存在的命令或过度重构 CMake。
---

# CK Build Helper

## 使用边界

当用户的问题与 CK Build 工程有关时，优先按本 Skill 回答，包括：

- 不知道如何配置、构建、编译、清理工程。
- 修改 `Kconfig`、`.config`、`ck_config.cmake`、`ck_config.h` 相关问题。
- 新增源码、头文件、静态库、package / 外部模块。
- 修改 `CMakeLists.txt`、`ck_project.cmake`、`ck_utils.cmake` 的小范围问题。
- 排查 CMake、Kconfig、工具链、Ninja、ARM GCC、链接脚本、启动文件、构建产物等简单错误。

不要把本 Skill 当成通用 CMake 教程。回答应优先遵守 CK Build 当前工程约定。

## 当前真实命令

CK Build 工程入口是工程目录下的 `ck_tool.py`。

只允许使用这些命令：

```bash
python ck_tool.py config
python ck_tool.py build
python ck_tool.py make
python ck_tool.py clean
python ck_tool.py auto
python ck_tool.py help
```

简写命令：

```bash
python ck_tool.py c
python ck_tool.py b
python ck_tool.py m
python ck_tool.py cl
python ck_tool.py a
python ck_tool.py h
```

命令含义：

- `config` / `c`：启动 Kconfig menuconfig，并生成 `ck_config.cmake`、`ck_config.h`。
- `build` / `b`：删除并重新创建构建目录，然后执行 Kconfig 中的 `CK_CMD_CONFIGURE`。
- `make` / `m`：执行 Kconfig 中的 `CK_CMD_BUILD`。如果 `CK_VERSION_ENABLE=y`，编译前更新版本宏。
- `clean` / `cl`：执行 Kconfig 中的 `CK_CMD_CLEAN`。
- `auto` / `a`：依次执行 `config -> build -> make`。
- `help` / `h`：显示帮助。

禁止编造这些命令：

- `rebuild`
- `menuconfig`
- `configure`
- `doctor`
- `new`
- `init`

如果用户想“重新构建”，推荐组合：

```bash
python ck_tool.py build
python ck_tool.py make
```

或者：

```bash
python ck_tool.py auto
```

## 三层边界

回答 CK Build 问题时，优先按三层结构解释：

1. Python 层：`ck_tool.py` 调用 `ck_tools/ck_core.py`，负责命令调度、Hook、执行 CMake/Kconfig 命令。
2. Kconfig 层：`Kconfig` 和 `.config` 负责配置项来源，导出给 Python、CMake、C/C++。
3. CMake 层：`CMakeLists.txt`、`ck_project.cmake`、`ck_utils.cmake` 负责源码扫描、编译参数、链接和产物生成。

不要建议用户绕过 Kconfig 直接硬编码所有配置。

## Kconfig 与生成文件关系

必须按这个关系说明：

```text
Kconfig + menuconfig
        ↓
.config
        ↓
ck_config.cmake  -> 给 CMake 使用
ck_config.h      -> 给 C / C++ 使用
```

修改建议：

- 修改 `Kconfig` 或配置选项后，执行：

```bash
python ck_tool.py config
```

- 修改 CMake 构建命令、工具链、生成器、工程类型后，通常再执行：

```bash
python ck_tool.py build
python ck_tool.py make
```

- 修改普通 `.c/.cpp/.h` 源码后，通常只需要：

```bash
python ck_tool.py make
```

## 关键 Kconfig 配置项

回答时优先识别这些配置项：

- `CK_TOOLS_ROOT`：`ck_tools` 所在路径。
- `CK_WORKSPACE_ROOT`：工作区路径，通常用于定位 `package`。
- `CK_PROJECT_TYPE`：工程类型，目前模板中常见为 `STANDARD`、`STM32CUBEMX`。
- `CK_CMD_CONFIGURE`：CMake 配置命令。
- `CK_CMD_BUILD`：编译命令。
- `CK_CMD_CLEAN`：清理命令。
- `CK_VERSION_ENABLE`：是否在 `make` 前更新版本宏。
- `PRO_NAME`：项目名 / 输出产物名。

不要随意改动 `CK_TOOLS_ROOT` 和 `CK_WORKSPACE_ROOT`，除非用户明确要移动工具目录或工作区目录。

## package 新增规则

推荐 package 目录结构：

```text
package/
└── xxx/
    ├── Kconfig
    ├── CMakeLists.txt
    ├── xxx.c
    └── xxx.h
```

package 总入口通常是：

```text
package/Kconfig
package/CMakeLists.txt
```

常见机制：

- `package/Kconfig` 可通过 `source "$(CK_WORKSPACE_ROOT)/package/*/Kconfig"` 自动引入一级 package 的 Kconfig。
- 单个 package 用 `menuconfig XXX` 定义是否启用。
- 单个 package 的 `CMakeLists.txt` 可用当前 CK Build 模板函数接入，例如 `module_template(XXX)`。

新增 package 的回答流程：

1. 先让用户确认 package 放在工作区 `package/xxx` 下。
2. 新增 `Kconfig`，定义启用开关。
3. 新增 `CMakeLists.txt`，使用现有模板函数接入源码。
4. 确认总 `package/Kconfig` 是否已经自动扫描。
5. 执行：

```bash
python ck_tool.py config
python ck_tool.py build
python ck_tool.py make
```

不要建议把 package 做成复杂 target 依赖树，除非用户明确要求。

## CMake 修改边界

修改 CMake 时必须保持 CK Build 风格：

- 优先使用项目已有的扫描函数和模板函数。
- 不要把简单工程强行改成复杂的 `add_library` / target 依赖树。
- 不要随意删除 `include(ck_config.cmake)`、`ck_project.cmake`、`ck_utils.cmake` 相关逻辑。
- 不要把 `arm-none-eabi-gcc`、`objcopy`、`objdump`、`size` 写死到通用模板里。
- STM32 工程要保留启动文件、链接脚本、CPU/FPU/float-abi、CMSIS/HAL 路径等关键路径。
- 标准工程和 STM32 工程应保持相近流程，但允许 STM32 保留必要的专用配置。

当用户只问“怎么新增源码”，优先建议：

- 放入已有会被扫描的源码目录；或
- 在对应模块 `CMakeLists.txt` 中用 CK Build 已有函数添加；或
- 必要时再手动加入源文件。

## Hook 使用边界

工程侧 `ck_tool.py` 只保留用户自定义 Hook。

可用 Hook：

- `before_config(ctx)` / `after_config(ctx)`
- `before_config_gen(ctx)` / `after_config_gen(ctx)`
- `before_build(ctx)` / `after_build(ctx)`
- `before_make(ctx)` / `after_make(ctx)`
- `before_clean(ctx)` / `after_clean(ctx)`
- `on_error(ctx, error)`

Hook 适合做：

- 构建前检查外部工具。
- 生成额外文件。
- 拷贝产物。
- 打印工程自定义信息。
- 错误时补充提示。

不要把大量通用构建逻辑重新塞回工程侧 `ck_tool.py`。

## 常见错误排查顺序

遇到错误日志时，按这个顺序排查：

1. 用户执行的命令是否真实存在。
2. 是否在工程目录执行 `python ck_tool.py xxx`。
3. 是否安装 `kconfiglib`。
4. `Kconfig` 中 `CK_TOOLS_ROOT` 是否能正确指向 `ck_tools`。
5. `CK_WORKSPACE_ROOT` 是否能正确指向工作区。
6. `.config` 是否存在，是否需要重新执行 `config`。
7. `ck_config.cmake`、`ck_config.h` 是否生成。
8. `CK_CMD_CONFIGURE` 中的 CMake 生成器是否已安装，例如 Ninja。
9. 工具链是否能被 CMake 找到。
10. STM32 工程是否缺启动文件、链接脚本、CPU/FPU 参数。
11. package 是否被 `package/Kconfig` 和 `package/CMakeLists.txt` 接入。
12. 构建目录是否需要重新执行 `build`。

## 回答风格

- 先指出问题属于配置、构建、编译、package、CMake 还是工具链。
- 优先给出最小修改方案。
- 涉及文件修改时，明确写出应该改哪个文件、哪一段。
- 不要长篇泛讲 CMake 理论。
- 不确定时，要求用户贴出对应文件或错误日志，不要猜不存在的命令。
- 如果需要给命令，只给当前 CK Build 真实支持的命令。
