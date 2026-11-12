"""Exercise the Video Factory workflow with a real MP4."""

import json
import shutil
import subprocess
import sys
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and ffprobe are required"
)
class VideoFactoryTest(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(TemporaryDirectory()))
        self.output = self.directory / "result.mp4"
        self.example = ROOT / "examples" / "project_constitution.example.json"

    def run_workflow(self, constitution):
        return subprocess.run(
            [
                sys.executable, "-B", str(ROOT / "workflows/video_factory/smoke_test.py"),
                str(constitution), str(self.output),
            ],
            capture_output=True,
            text=True,
        )

    def approved_constitution(self, limit):
        data = json.loads(self.example.read_text(encoding="utf-8"))
        data["governance"].update(status="approved", approved_at="2026-11-12T12:00:00Z")
        data["rule_assignments"][0]["parameters"]["max_duration"] = limit
        path = self.directory / "approved.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_approved_video_at_limit_is_decodable(self):
        result = self.run_workflow(self.approved_constitution(2))
        self.assertEqual(result.returncode, 0, result.stderr)
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-xerror", "-i", str(self.output), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(decoded.returncode, 0, decoded.stderr)

    def test_over_limit_video_leaves_no_output(self):
        result = self.run_workflow(self.approved_constitution(1))
        self.assertEqual(result.returncode, 1)
        self.assertIn("exceeds 1s", result.stderr)
        self.assertFalse(self.output.exists())

    def test_draft_leaves_no_output(self):
        result = self.run_workflow(self.example)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires an approved constitution", result.stderr)
        self.assertFalse(self.output.exists())
