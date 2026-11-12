"""Exercise the production CLI using the checked-in project example."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProductionTest(unittest.TestCase):
    def setUp(self):
        self.example = ROOT / "examples" / "project_constitution.example.json"
        constitution = json.loads(self.example.read_text(encoding="utf-8"))
        constitution["governance"].update(
            status="approved", approved_at="2026-11-12T12:00:00Z"
        )
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.approved = Path(directory) / "approved.json"
        self.approved.write_text(json.dumps(constitution), encoding="utf-8")

    def run_check(self, path, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_production.py"), str(path), *args],
            capture_output=True,
            text=True,
        )

    def test_approved_constitution_allows_launch(self):
        result = self.run_check(self.approved)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_draft_blocks_launch(self):
        result = self.run_check(self.example)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires an approved constitution", result.stderr)

    def test_deliverable_at_limit_passes(self):
        result = self.run_check(self.approved, "--duration-seconds", "240")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_deliverable_over_limit_fails(self):
        result = self.run_check(self.approved, "--duration-seconds", "240.001")
        self.assertEqual(result.returncode, 1)
        self.assertIn("exceeds 240s", result.stderr)
