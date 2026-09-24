#!/usr/bin/env python3
"""JOS repository quality gate.

Validates repository structure and JOS examples against the canonical JSON
Schema. This is intentionally small and deterministic so it can run in CI.
"""

from __future__ import annotations

import json
import pathlib
import sys

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLICY = ROOT / "quality" / "repository-policy.v1.json"
SCHEMA = ROOT / "schema" / "jos.schema.json"

BLOCKERS: list[str] = []
WARNINGS: list[str] = []


def blocker(message: str) -> None:
    BLOCKERS.append(message)


def warning(message: str) -> None:
    WARNINGS.append(message)


def load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        blocker(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def check_required_files(policy: dict) -> None:
    spec = policy["classes"]["SPEC"]
    required = list(spec["required_files"]) + [
        "SPECIFICATION.md",
        "IANA.md",
        "CONFORMANCE.md",
        "QUALITY-GATES.md",
        "schema/jos.schema.json",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            blocker(f"missing required SPEC artifact: {rel}")


def check_schema(schema: dict | None) -> Draft202012Validator | None:
    if schema is None:
        return None
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        blocker("schema/jos.schema.json must declare JSON Schema Draft 2020-12")
    try:
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema)
    except Exception as exc:
        blocker(f"schema/jos.schema.json is not a valid Draft 2020-12 schema: {exc}")
        return None


def check_examples(validator: Draft202012Validator | None) -> None:
    examples_dir = ROOT / "examples"
    if not examples_dir.exists():
        blocker("examples/ directory is missing")
        return

    examples = sorted(examples_dir.rglob("*.jos"))
    if not examples:
        blocker("no .jos examples found")
        return

    for path in examples:
        doc = load_json(path)
        if doc is None or validator is None:
            continue
        errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
        for err in errors:
            location = "/".join(str(p) for p in err.absolute_path) or "<root>"
            blocker(f"{path.relative_to(ROOT)}:{location}: {err.message}")


def check_current_mime() -> None:
    forbidden = "application/vnd.josfox+json"
    current_docs = [
        ROOT / "README.md",
        ROOT / "SPECIFICATION.md",
        ROOT / "IANA.md",
        ROOT / "CONFORMANCE.md",
        ROOT / "SECURITY.md",
    ]
    for path in current_docs:
        if path.exists() and forbidden in path.read_text(encoding="utf-8"):
            blocker(f"{path.relative_to(ROOT)} contains deprecated media type {forbidden}")


def check_authority_links() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "application/vnd.jos+json" not in readme:
        blocker("README.md does not declare application/vnd.jos+json")
    if "SPECIFICATION.md" not in readme:
        blocker("README.md does not link to the normative specification")
    if "schema/jos.schema.json" not in readme:
        blocker("README.md does not link to the canonical schema")


def main() -> int:
    policy = load_json(POLICY)
    schema = load_json(SCHEMA)

    if policy is not None:
        check_required_files(policy)
    validator = check_schema(schema)
    check_examples(validator)
    check_current_mime()
    check_authority_links()

    for item in WARNINGS:
        print(f"WARNING: {item}")
    for item in BLOCKERS:
        print(f"BLOCKER: {item}")

    if BLOCKERS:
        print(f"FAIL: {len(BLOCKERS)} blocker(s), {len(WARNINGS)} warning(s)")
        return 1

    result = "PASS_WITH_WARNINGS" if WARNINGS else "PASS"
    print(f"{result}: 0 blockers, {len(WARNINGS)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
