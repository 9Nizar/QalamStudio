"""Produce and validate a synthetic MP4 for a Video Factory smoke test."""

import argparse
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constitution", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".mp4" or args.output.exists():
        parser.error("output must be a new .mp4 file")

    check = [
        sys.executable, "-B", str(ROOT / "scripts" / "check_production.py"),
        str(args.constitution.resolve()),
    ]
    try:
        subprocess.run(check, check=True)
        with TemporaryDirectory(dir=args.output.resolve().parent) as directory:
            video = Path(directory) / "smoke-test.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc2=size=640x360:rate=24", "-t", "2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video),
                ],
                check=True,
            )
            subprocess.run([*check, "--video", str(video)], check=True)
            args.output.hardlink_to(video)
    except (OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Video Factory smoke test failed: {error}\n")
    print(f"Validated MP4 saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()
