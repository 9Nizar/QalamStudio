"""Exercise narrated exports with a short generated clip and WAV."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and ffprobe are required"
)
class NarratedExportTest(unittest.TestCase):
    def test_narration_is_padded_and_overrun_is_rejected(self):
        directory = Path(self.enterContext(TemporaryDirectory()))
        example = ROOT / "examples/project_constitution.example.json"
        data = json.loads(example.read_text(encoding="utf-8"))
        data["governance"].update(status="approved", approved_at="2026-11-12T12:00:00Z")
        constitution = directory / "approved.json"
        constitution.write_text(json.dumps(data), encoding="utf-8")
        manifest = directory / "shots.json"
        manifest.write_text('[{"source":"clip.mp4","frames":24}]', encoding="utf-8")
        for source, output in [
            ("color=blue:s=320x180:r=24:d=1", "clip.mp4"),
            ("sine=frequency=440:duration=0.25", "voice.wav"),
        ]:
            subprocess.run(
                ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", source, str(directory / output)],
                check=True,
            )

        command = [
            sys.executable, "-B", str(ROOT / "workflows/video_factory/render.py"),
            str(constitution), str(manifest), str(directory / "voice.wav"),
        ]
        output = directory / "narrated.mp4"
        result = subprocess.run(
            [*command, str(output), "--narration-offset-ms", "250"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        audio = subprocess.check_output([
            "ffmpeg", "-v", "error", "-i", str(output), "-map", "0:a:0",
            "-ar", "8000", "-f", "s16le", "-",
        ])
        self.assertGreaterEqual(len(audio), 16000)
        self.assertEqual(set(audio[:1600]), {0})
        self.assertTrue(any(audio[4800:6400]))
        self.assertEqual(set(audio[12800:16000]), {0})

        rejected = directory / "rejected.mp4"
        result = subprocess.run(
            [*command, str(rejected), "--narration-offset-ms", "800"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Narration plus offset exceeds", result.stderr)
        self.assertFalse(rejected.exists())
