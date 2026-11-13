"""Render an approved shot list with narration and optional open captions."""

import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


WORKFLOW = Path(__file__).resolve().parent
ROOT = WORKFLOW.parents[1]


def duration(path, stream, entry):
    value = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", entry, "-of", "csv=p=0", str(path)],
        text=True, timeout=30,
    ).strip()
    seconds = Decimal(value)
    if not seconds.is_finite() or seconds <= 0:
        raise ValueError(f"No positive duration found in {path.name}.")
    return seconds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constitution", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("narration", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--subtitles", type=Path)
    parser.add_argument("--narration-offset-ms", type=int, default=0)
    parser.add_argument("--ambience", type=Path, help="Optional background audio.")
    parser.add_argument("--ambience-gain", type=float, default=0.15)
    args = parser.parse_args()
    if not 0 <= args.ambience_gain <= 1:
        parser.error("--ambience-gain must be between 0 and 1.")
    output = args.output.absolute()
    if output.suffix.lower() != ".mp4" or output.exists():
        parser.error("Choose a new .mp4 output path.")
    if args.narration_offset_ms < 0:
        parser.error("--narration-offset-ms must be nonnegative.")

    python = [sys.executable, "-B"]
    try:
        with TemporaryDirectory(dir=output.parent) as directory:
            scratch = Path(directory)
            picture = scratch / "picture.mp4"
            staged = scratch / "render.mp4"
            subprocess.run(
                [*python, str(WORKFLOW / "assemble.py"), str(args.constitution.resolve()),
                 str(args.manifest.resolve()), str(picture)],
                check=True,
            )
            length = duration(picture, "v:0", "stream=duration")
            narration = args.narration.resolve(strict=True)
            voice_length = duration(narration, "a:0", "stream=duration")
            offset = Decimal(args.narration_offset_ms) / 1000
            if voice_length + offset > length:
                raise ValueError("Narration plus offset exceeds the assembled video duration.")

            video_options = ["-c:v", "copy"]
            if args.subtitles is not None:
                shutil.copyfile(args.subtitles, scratch / "captions.srt")
                video_options = [
                    "-vf", "subtitles=captions.srt:"
                    "force_style='FontName=Arial,FontSize=12,Outline=1.5,Shadow=0,MarginV=30'",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                ]
            audio_inputs = []
            voice_filter = f"adelay={args.narration_offset_ms}:all=1,apad"
            audio_options = ["-map", "1:a:0", "-af", voice_filter]
            if args.ambience is not None:
                audio_inputs = ["-i", str(args.ambience.resolve(strict=True))]
                audio_options = [
                    "-filter_complex",
                    f"[1:a:0]{voice_filter}[voice];"
                    f"[2:a:0]volume={args.ambience_gain}[bed];"
                    "[voice][bed]amix=inputs=2:duration=first:normalize=0,"
                    "alimiter=limit=0.95:level=0:latency=1[mix]",
                    "-map", "[mix]",
                ]
            subprocess.run(
                ["ffmpeg", "-v", "error", "-xerror", "-i", str(picture), "-i", str(narration),
                 *audio_inputs, "-map", "0:v:0", *video_options, *audio_options,
                 "-c:a", "aac", "-b:a", "128k", "-t", format(length, "f"),
                 "-movflags", "+faststart", str(staged)],
                cwd=scratch, check=True,
            )
            subprocess.run(
                [*python, str(ROOT / "scripts/check_production.py"),
                 str(args.constitution.resolve()), "--video", str(staged)],
                check=True,
            )
            subprocess.run(
                ["ffmpeg", "-v", "error", "-xerror", "-i", str(staged), "-f", "null", "-"],
                check=True,
            )
            output.hardlink_to(staged)
    except (OSError, ValueError, InvalidOperation, subprocess.SubprocessError) as error:
        parser.exit(1, f"Narrated export failed: {error}\n")
    print(f"Validated MP4 saved to {output}")


if __name__ == "__main__":
    main()
