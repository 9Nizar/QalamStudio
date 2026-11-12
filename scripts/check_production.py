"""Check a constitution before launch and optionally validate a measured runtime."""

import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path

from jsonschema.exceptions import ValidationError

from validate_project_constitution import read_json, validate_constitution


def check_production(constitution, duration=None):
    rules = validate_constitution(constitution)
    if constitution["governance"]["status"] != "approved":
        raise ValueError("Production requires an approved constitution.")
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
    parser.add_argument("--duration-seconds", type=Decimal)
    try:
        args = parser.parse_args()
        check_production(read_json(args.constitution), args.duration_seconds)
    except (OSError, ValueError, ValidationError, InvalidOperation) as error:
        parser.exit(1, f"Production check failed: {error}\n")
    print("Production check passed.")


if __name__ == "__main__":
    main()
