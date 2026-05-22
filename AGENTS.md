# Repository Guidelines

## Project Structure & Module Organization

This repository provides a CMake + Kconfig build scaffold for C and embedded projects. Shared build helpers live in `ck_tools/`, including Python scripts, CMake helper functions, and Kconfig tooling. Project templates are under `template/`: `template/project/stm32_test/` is the STM32/Ninja example, `template/test/template/` is a smaller host/test template, `template/package/` contains reusable packages such as `unity` and `sum_mod`, and `template/driver/` contains driver modules. Offline Windows tools and wheels are stored in `ware/`; reference documents are in `doc/`.

## Build, Test, and Development Commands

Run commands from the specific generated project directory, such as `template/project/stm32_test/` or `template/test/template/`.

- `python ck_tool.py config` opens Kconfig/menuconfig and regenerates config outputs.
- `python ck_tool.py build` configures CMake into `build/`; the STM32 template uses Ninja and `cmake/gcc-arm-none-eabi.cmake`.
- `python ck_tool.py make` builds the configured project and writes artifacts to `bin/`.
- `python ck_tool.py clean` runs the backend clean target.
- `python ck_tool.py auto` runs config, configure, and build in sequence where supported.
- `ctest --test-dir build` runs CTest tests for templates that enable `PRO_TEST_UNIT` or `PRO_TEST_INTEGRATION`.

## Coding Style & Naming Conventions

Use 4-space indentation for Python and CMake edits. Match surrounding C style in generated STM32 files, and keep user code inside STM32 `USER CODE BEGIN/END` regions. Name C modules with lowercase descriptive filenames, for example `my_sum.c` and `drv1.c`. Keep Kconfig/CMake symbols uppercase and scoped, for example `SUM_MOD` or `DRV_DRV1`. Prefer existing helper APIs such as `module_template()`, `list_template()`, and `set_external_path()` over duplicating source discovery logic.

## Testing Guidelines

Use Unity sources in `template/package/unity/` for unit-style C tests. Test-enabled templates should register tests through CMake with names like `${PRO_NAME}_unit` or `${PRO_NAME}_integration`. Before submitting build-system changes, verify at least one representative template with `python ck_tool.py build` and `python ck_tool.py make`; run `ctest --test-dir build` when tests are enabled.

## Commit & Pull Request Guidelines

The Git history uses short, direct Chinese commit messages, often describing the result, such as adding a demo module or fixing generated config inclusion. Follow that style: keep commits concise, action-oriented, and scoped to one change. Pull requests should describe the affected template/tooling path, list tested commands, mention required toolchain assumptions, and include screenshots only for GUI/menuconfig changes.

## Security & Configuration Tips

Do not commit local `build/` or `bin/` outputs unless they are intentional template artifacts. Keep machine-specific compiler, OpenOCD, and TFTP paths out of shared files; document required local setup in the PR instead.
