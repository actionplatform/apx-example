"""Drive the plugin through the core's registry without installing it."""

import asyncio
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from action_platform.core.flow import gitflow
from action_platform.core.scaffold.catalog import Matrix, with_plugin_clouds
from action_platform.core.wiring import wired
from action_platform.plugins import Loaded, Plugins, PluginState, registry

from apx_example import ExamplePlugin
from apx_example.release import Calver, Plain


class ExamplePluginTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.plugins = Plugins(
            [Loaded(ExamplePlugin(), "apx-example-example", "0.1.0")],
            PluginState(file=Path(self.tmp.name) / "plugins.json"),
        )
        registry._current = self.plugins
        self.addCleanup(registry.reset)
        self.addCleanup(wired.restore, "gitflow_rules")
        self.addCleanup(self.tmp.cleanup)

    def test_tool_is_prefixed_and_answers(self):
        from action_platform.mcp import server

        mcp = server.build()
        names = {t.name for t in asyncio.run(mcp.list_tools())}

        self.assertIn("example_hello", names)

        result = asyncio.run(mcp.call_tool("example_hello", {"name": "you"}))

        self.assertEqual(json.loads(result.content[0].text)["greeting"], "hello you")

    def test_rules_are_replaced_while_enabled(self):
        self.plugins.register()

        self.assertIsNotNone(gitflow.check_branch("chore/1"))

        self.plugins.disable("example")

        self.assertIsNone(gitflow.check_branch("chore/1"))

    def test_overlay_joins_the_matrix(self):
        merged = with_plugin_clouds(Matrix.from_dict({"clouds": []}))

        self.assertEqual([c.name for c in merged.clouds], ["example"])
        self.assertEqual(merged.cloud("example").source, "example")

    def test_release_providers(self):
        self.assertTrue(Calver().next("1.0.0", "patch", False, []).count(".") == 2)
        self.assertIn("- feat: x", Plain().render("1.0.0", ["feat: x"]))


class TargetTest(unittest.TestCase):
    def test_readiness_names_the_overlay(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from action_platform.core.context import Context

        from apx_example.target import ExampleTarget

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = ExampleTarget().readiness(Context(repo_root=root, stage="dev"))
            (root / "deploy").mkdir()
            (root / "deploy" / "run.sh").write_text("#!/bin/sh\necho ok\n")
            present = ExampleTarget().readiness(Context(repo_root=root, stage="dev"))

        self.assertFalse(missing[0].ok)
        self.assertEqual(missing[0].fix, "action-platform cloud set example")
        self.assertTrue(present[0].ok)
