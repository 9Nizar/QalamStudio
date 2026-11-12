"""Check a constitution before launch and optionally validate a measured runtime."""

import argparse
import json
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path

from jsonschema.exceptions import ValidationError

from validate_project_constitution import read_json, validate_constitution


def video_duration(path):
    path = path.resolve(strict=True)
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "V:0",
            "-show_entries", "stream=index:format=duration", "-of", "json", str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise ValueError(f"Cannot read video {path.name}: {result.stderr.strip()}")
    metadata = json.loads(result.stdout)
    duration = metadata.get("format", {}).get("duration")
    if not metadata.get("streams") or duration in (None, "N/A"):
        raise ValueError(f"No video stream with a measurable duration in {path.name}.")
    return Decimal(duration)


def check_production(constitution, duration=None, *, video=None):
    rules = validate_constitution(constitution)
    if constitution["governance"]["status"] != "approved":
        raise ValueError("Production requires an approved constitution.")
    if video is not None:
        duration = video_duration(video)
    if duration is None:
        return
    if not duration.is_finite() or duration <= 0:
        raise ValueError("Deliverable duration must be finite and positive.")

    for assignment in constitution["rule_assignments"]:
        rule_id = assignment["rule_id"]
        if rule_id == "RULE-MAX-DURATION" and assignment["enabled"] and rules[rule_id]["enabled"]:
            limit = assignment["parameters"]["max_duration"]
            if duration > limit:
                raise ValueError(f"{assignment['id']}: duration {duration}s exceeds {limit}s.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("constitution", type=Path)
    duration_input = parser.add_mutually_exclusive_group()
    duration_input.add_argument("--duration-seconds", type=Decimal)
    duration_input.add_argument("--video", type=Path, help="Measure a local video using ffprobe.")
    try:
        args = parser.parse_args()
        check_production(read_json(args.constitution), args.duration_seconds, video=args.video)
    except (OSError, ValueError, ValidationError, InvalidOperation, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"Production check failed: {error}\n")
    print("Production check passed.")


if __name__ == "__main__":
    main()
