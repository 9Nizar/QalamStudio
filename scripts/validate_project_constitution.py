"""Validate the rule catalog and the project constitution example."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    schemas = {
        name: read_json(ROOT / "schemas" / f"{name}.schema.json")
        for name in ("project_rule", "project_rule_assignment", "project_constitution")
    }
    registry = Registry()
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))

    rule_validator = Draft202012Validator(schemas["project_rule"])
    rules = read_json(ROOT / "knowledge" / "rules.json")
    if not isinstance(rules, list):
        raise ValueError("The rule catalog must be a JSON array.")

    rule_ids = set()
    for rule in rules:
        rule_validator.validate(rule)
        rule_id = rule["id"]
        if rule_id in rule_ids:
            raise ValueError(f"Duplicate rule ID: {rule_id}")
        rule_ids.add(rule_id)

    example = read_json(ROOT / "examples" / "project_constitution.example.json")
    constitution_validator = Draft202012Validator(
        schemas["project_constitution"],
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    constitution_validator.validate(example)
    for assignment in example["rule_assignments"]:
        rule_id = assignment["rule_id"]
        if rule_id not in rule_ids:
            raise ValueError(f"Unknown rule ID: {rule_id}")

        if rule_id == "RULE-MAX-DURATION":
            parameters = assignment["parameters"]
            duration = parameters.get("max_duration")
            if type(duration) is not int or duration <= 0:
                raise ValueError(f'{assignment["id"]}: max_duration must be a positive integer.')
            if parameters.get("unit") != "seconds":
                raise ValueError(f'{assignment["id"]}: unit must be "seconds".')

    print("Project constitution and rule catalog validated.")


if __name__ == "__main__":
    main()
