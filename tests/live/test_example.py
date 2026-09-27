"""Against the real destination, when its credentials are in the environment — skipped anywhere else. apx-dokploy's live suite installs Dokploy on the CI runner; do the same for your cloud, or point these at a sandbox account."""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from action_platform.core.context import Context

from apx_example.target import ExampleTarget

LIVE = bool(os.environ.get("EXAMPLE_LIVE"))


@unittest.skipUnless(LIVE, "needs the real destination: EXAMPLE_LIVE=1")
class LiveTest(unittest.TestCase):
    def test_deploy_then_delete(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "deploy").mkdir()
            (root / "deploy" / "run.sh").write_text("#!/bin/sh\necho live\n")
            ctx = Context(repo_root=root, stage="ci", next_version="0.0.1")
            target = ExampleTarget()

            self.assertTrue(target.deploy(ctx).ok)
            self.assertTrue(target.verify("0.0.1", "ci"))

            target.delete(ctx)

            self.assertFalse(target.verify("0.0.1", "ci"))
