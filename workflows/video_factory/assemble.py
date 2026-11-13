"""Assemble ordered local video segments into a validated silent MP4."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constitution", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".mp4" or args.output.exists():
        parser.error("output must be a new .mp4 file")

    check = [
        sys.executable, "-B", str(ROOT / "scripts/check_production.py"),
        str(args.constitution.resolve()),
    ]
    try:
        subprocess.run(check, check=True)
        shots = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
        if not isinstance(shots, list) or not shots:
            raise ValueError("manifest must be a nonempty array of shots")
        with TemporaryDirectory(dir=args.output.resolve().parent) as directory:
            scratch = Path(directory)
            entries = []
            for index, shot in enumerate(shots):
                if not isinstance(shot, dict) or not isinstance(shot.get("source"), str):
                    raise ValueError(f"shot {index + 1} requires a source path")
                start = shot.get("start_frames", 0)
                count = shot.get("frames")
                if type(start) is not int or start < 0 or type(count) is not int or count < 1:
                    raise ValueError(f"shot {index + 1} requires nonnegative start_frames and positive frames")
                source = (args.manifest.parent / shot["source"]).resolve(strict=True)
                clip = scratch / f"shot-{index}.mp4"
                subprocess.run(
                    [
                        "ffmpeg", "-v", "error", "-xerror", "-i", str(source),
                        "-map", "0:V:0", "-an", "-vf",
                        f"fps=24,trim=start_frame={start}:end_frame={start + count},"
                        "setpts=PTS-STARTPTS,scale=720:1280:force_original_aspect_ratio=decrease,"
                        "pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip),
                    ],
                    check=True,
                )
                frames = subprocess.check_output(
                    ["ffprobe", "-v", "error", "-select_streams", "v:0",
                     "-show_entries", "stream=nb_frames", "-of", "csv=p=0", str(clip)],
                    text=True,
                ).strip()
                if frames != str(count):
                    raise ValueError(f"shot {index + 1} is shorter than the requested range")
                entries.append(f"file '{clip.name}'\n")

            playlist = scratch / "shots.txt"
            playlist.write_text("".join(entries), encoding="ascii")
            staged = scratch / "assembled.mp4"
            subprocess.run(
                ["ffmpeg", "-v", "error", "-f", "concat", "-safe", "1", "-i", str(playlist),
                 "-c", "copy", "-movflags", "+faststart", str(staged)],
                check=True,
            )
            subprocess.run([*check, "--video", str(staged)], check=True)
            args.output.hardlink_to(staged)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Video assembly failed: {error}\n")
    print(f"Validated MP4 saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()
