"""验证模板和共享核心的失败退出，所有构建产物限制在临时工程中。"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ck_tools import ck_core, ck_version


class FailureStatusTests(unittest.TestCase):
    def setUp(self):
        self.environment = mock.patch.dict(os.environ)
        self.environment.start()
        self.temporary = tempfile.TemporaryDirectory(prefix="ck-build-status-")
        self.project = Path(self.temporary.name)
        self.write_project()

    def tearDown(self):
        self.temporary.cleanup()
        self.environment.stop()

    def write_project(self, configure_status=0, make_status=0, clean_status=0, version=False):
        # 使用真实子进程记录执行阶段，验证失败后确实没有启动后续命令。
        (self.project / "command.py").write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "with Path('steps.txt').open('a', encoding='utf-8') as output:\n"
            "    output.write(sys.argv[1] + '\\n')\n"
            "print(sys.argv[1])\n"
            "sys.exit(int(sys.argv[2]))\n",
            encoding="utf-8",
        )
        python = Path(sys.executable).as_posix()
        symbols = {
            "CK_TOOLS_ROOT": REPO_ROOT.as_posix(),
            "CK_WORKSPACE_ROOT": self.project.as_posix(),
            "CK_BUILD_DIR": "build",
            "CK_CMD_CONFIGURE": f'"{python}" command.py configure {configure_status}',
            "CK_CMD_BUILD": f'"{python}" command.py make {make_status}',
            "CK_CMD_CLEAN": f'"{python}" command.py clean {clean_status}',
        }
        kconfig = 'mainmenu "Failure status test"\n'
        for name, value in symbols.items():
            kconfig += f"config {name}\n    string\n    default {json.dumps(value)}\n"
        kconfig += 'config CK_VERSION_ENABLE\n    bool "Enable version update"\n    default n\n'
        (self.project / "Kconfig").write_text(kconfig, encoding="utf-8")
        (self.project / ".config").write_text(
            "CONFIG_CK_VERSION_ENABLE=y\n" if version else "# CONFIG_CK_VERSION_ENABLE is not set\n",
            encoding="utf-8",
        )

    def steps(self):
        output = self.project / "steps.txt"
        return output.read_text(encoding="utf-8").splitlines() if output.exists() else []

    def tool(self, hooks=None):
        return ck_core.CKTool(self.project, hooks=hooks, logger=lambda message: None)

    def run_template(self, template, command):
        # 复制入口而非整个硬件模板，保留模板的真实 Kconfig 加载与 CLI 调度。
        source = REPO_ROOT / "template/project" / template / "ck_tool.py"
        (self.project / "ck_tool.py").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run(
            [sys.executable, "ck_tool.py", command], cwd=self.project,
            env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15,
        )

    def test_both_templates_return_nonzero_when_build_make_or_clean_fails(self):
        for template in ("standard_project", "stm32_project"):
            for command in ("build", "make", "clean"):
                with self.subTest(template=template, command=command):
                    self.write_project(configure_status=7, make_status=8, clean_status=9)
                    result = self.run_template(template, command)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("Error:", result.stdout)

    def test_both_templates_return_zero_for_success(self):
        for template in ("standard_project", "stm32_project"):
            for command in ("build", "make", "clean"):
                with self.subTest(template=template, command=command):
                    result = self.run_template(template, command)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_both_templates_return_nonzero_when_program_cannot_start(self):
        text = (self.project / "Kconfig").read_text(encoding="utf-8")
        text = text.replace(
            json.dumps(f'"{Path(sys.executable).as_posix()}" command.py make 0'),
            json.dumps('"./missing-build-executable"'),
        )
        (self.project / "Kconfig").write_text(text, encoding="utf-8")
        for template in ("standard_project", "stm32_project"):
            with self.subTest(template=template):
                result = self.run_template(template, "make")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.steps(), [])

    def test_auto_stops_before_make_and_after_hook_on_configure_failure(self):
        self.write_project(configure_status=7)
        hooks = mock.Mock(spec=ck_core.CKHooks)
        tool = self.tool(hooks)
        # 跳过交互界面，但仍执行真实配置生成和构建子进程。
        with mock.patch.object(tool, "_run_menuconfig"):
            with self.assertRaises(subprocess.CalledProcessError):
                tool.config(auto=True)
        self.assertEqual(self.steps(), ["configure"])
        hooks.after_build.assert_not_called()
        hooks.before_make.assert_not_called()

    def test_cli_reports_auto_failure_to_error_hook(self):
        self.write_project(configure_status=7)
        hooks = mock.Mock(spec=ck_core.CKHooks)
        fake_menu = types.SimpleNamespace(menuconfig=lambda kconf: None)
        with mock.patch.dict(sys.modules, {"menuconfig": fake_menu}):
            with self.assertRaises(SystemExit) as failed:
                ck_core.cli_main(self.project, hooks=hooks, logger=lambda message: None, argv=["auto"])
        self.assertEqual(failed.exception.code, 1)
        self.assertEqual(self.steps(), ["configure"])
        self.assertIsInstance(hooks.on_error.call_args.args[1], subprocess.CalledProcessError)

    def test_auto_runs_all_steps_on_success(self):
        tool = self.tool()
        with mock.patch.object(tool, "_run_menuconfig"):
            tool.config(auto=True)
        self.assertEqual(self.steps(), ["configure", "make"])

    def test_config_generation_failure_stops_auto(self):
        tool = self.tool()
        with mock.patch.object(tool, "_run_menuconfig"), mock.patch.object(
            ck_core, "generate_config", side_effect=OSError("cannot write generated config"),
        ):
            with self.assertRaises(OSError):
                tool.config(auto=True)
        self.assertEqual(self.steps(), [])

    def test_hook_failure_stops_before_command(self):
        hooks = mock.Mock(spec=ck_core.CKHooks)
        hooks.before_make.side_effect = RuntimeError("required environment missing")
        with self.assertRaises(RuntimeError):
            self.tool(hooks).make()
        self.assertEqual(self.steps(), [])
        hooks.after_make.assert_not_called()

    def test_version_update_failure_stops_make(self):
        self.write_project(version=True)
        hooks = mock.Mock(spec=ck_core.CKHooks)
        with mock.patch.object(ck_core, "update_ck_version_h", return_value=False):
            with self.assertRaisesRegex(RuntimeError, "Failed to update CK version"):
                self.tool(hooks).make()
        self.assertEqual(self.steps(), [])
        hooks.after_make.assert_not_called()

    def test_both_templates_fail_when_enabled_version_update_cannot_complete(self):
        self.write_project(version=True)
        for template in ("standard_project", "stm32_project"):
            with self.subTest(template=template):
                result = self.run_template(template, "make")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Failed to update CK version", result.stdout)
                self.assertEqual(self.steps(), [])

    def test_successful_version_update_allows_make(self):
        self.write_project(version=True)
        with mock.patch.object(ck_core, "update_ck_version_h", return_value=True):
            self.tool().make()
        self.assertEqual(self.steps(), ["make"])

    def test_disabled_version_update_does_not_require_git(self):
        with mock.patch.object(ck_core, "update_ck_version_h") as version:
            self.tool().make()
        version.assert_not_called()
        self.assertEqual(self.steps(), ["make"])

    def test_standalone_version_script_returns_failure_status(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "ck_tools/ck_version.py"),
             "--header", str(self.project / "missing.h"), "--work-dir", str(self.project)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_standalone_version_script_success_does_not_exit_with_error(self):
        with mock.patch.object(ck_version, "update_ck_version_h", return_value=True):
            ck_version.main(["--header", str(self.project / "ck_config.h")])


if __name__ == "__main__":
    unittest.main()
