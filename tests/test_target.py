import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from action_platform.core.context import Context

from apx_example.target import ExampleTarget, Parts
from tests.fake import FakeCloud


class FakeTarget(ExampleTarget):
    def __init__(self, cloud: FakeCloud) -> None:
        super().__init__()
        self.cloud = cloud

    def parts(self, spec):
        return Parts(cloud=self.cloud)


class TargetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def ctx(self, stage="dev", version="1.0.0"):
        return Context(repo_root=self.root, stage=stage, next_version=version)

    def test_deploy_ships_the_version_to_the_scope_and_verify_sees_it(self):
        cloud = FakeCloud()
        target = FakeTarget(cloud)

        result = target.deploy(self.ctx(version="1.2.0"))

        self.assertTrue(result.ok)
        self.assertEqual(result.url, "https://dev.example.test")
        self.assertTrue(target.verify("1.2.0", "dev"))
        self.assertFalse(target.verify("1.2.0", "prod"))

    def test_a_failed_ship_is_a_failed_result_with_the_reason(self):
        result = FakeTarget(FakeCloud(fails="quota exceeded")).deploy(self.ctx())

        self.assertFalse(result.ok)
        self.assertIn("quota exceeded", result.error)

    def test_diagnose_and_delete(self):
        target = FakeTarget(FakeCloud())
        target.deploy(self.ctx())

        self.assertEqual(target.diagnose(self.ctx()).version, "1.0.0")

        target.delete(self.ctx())

        self.assertEqual(target.diagnose(self.ctx()).status, "missing")

    def test_readiness_names_the_overlay(self):
        missing = ExampleTarget().readiness(self.ctx())
        (self.root / "deploy").mkdir()
        (self.root / "deploy" / "run.sh").write_text("#!/bin/sh\necho ok\n")
        present = ExampleTarget().readiness(self.ctx())

        self.assertFalse(missing[0].ok)
        self.assertEqual(missing[0].fix, "action-platform cloud set example")
        self.assertTrue(present[0].ok)

    def test_the_script_cloud_runs_the_overlay_and_remembers_the_version(self):
        (self.root / "deploy").mkdir()
        (self.root / "deploy" / "run.sh").write_text(
            '#!/bin/sh\necho "$SCOPE $VERSION"\n'
        )
        target = ExampleTarget()

        self.assertTrue(target.deploy(self.ctx(version="2.0.0")).ok)
        self.assertTrue(target.verify("2.0.0", "dev"))

    def test_a_failing_script_fails_the_deploy(self):
        (self.root / "deploy").mkdir()
        (self.root / "deploy" / "run.sh").write_text("#!/bin/sh\necho broken; exit 3\n")

        result = ExampleTarget().deploy(self.ctx())

        self.assertFalse(result.ok)
        self.assertIn("broken", result.error)
