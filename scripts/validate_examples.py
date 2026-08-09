#!/usr/bin/env python3
"""Validate example detection packages against the DPS spec.

Interim lint until the standalone validator CLI exists. Checks every
package under examples/:
  - package.yml parses, has apiVersion dps/v1 and kind DetectionPackage
  - required metadata fields (name, version semver, title, description,
    license, authors) are present; metadata.name matches the directory
  - spec.category / spec.severity / spec.telemetry / spec.targets present
  - every spec.rules entry points at an existing rule file with a
    unique UUID id, and the rule file's own id/logsource match
  - rule files parse and carry title/id/status/description/logsource/
    detection (with condition)/level
  - integrity.contentHash is a well-formed sha256 pin

Exits non-zero with a per-package error report on any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

RULE_REQUIRED = ["title", "id", "status", "description", "logsource", "detection", "level"]


def load_yaml(path: Path, errors: list[str]):
    try:
        with path.open() as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        errors.append(f"{path.relative_to(ROOT)}: YAML parse error: {exc}")
        return None


def validate_package(pkg_dir: Path, errors: list[str], seen_rule_ids: dict[str, str]) -> None:
    rel = pkg_dir.relative_to(ROOT)
    manifest_path = pkg_dir / "package.yml"
    if not manifest_path.is_file():
        errors.append(f"{rel}: missing package.yml")
        return
    doc = load_yaml(manifest_path, errors)
    if not isinstance(doc, dict):
        if doc is not None:
            errors.append(f"{rel}/package.yml: top level must be a mapping")
        return

    if doc.get("apiVersion") != "dps/v1":
        errors.append(f"{rel}/package.yml: apiVersion must be 'dps/v1'")
    if doc.get("kind") != "DetectionPackage":
        errors.append(f"{rel}/package.yml: kind must be 'DetectionPackage'")

    meta = doc.get("metadata")
    if not isinstance(meta, dict):
        errors.append(f"{rel}/package.yml: metadata missing or not a mapping")
        meta = {}
    for field in ("name", "version", "title", "description", "license", "authors"):
        if not meta.get(field):
            errors.append(f"{rel}/package.yml: metadata.{field} is required")
    if meta.get("name") and meta["name"] != pkg_dir.name:
        errors.append(
            f"{rel}/package.yml: metadata.name '{meta['name']}' must match directory '{pkg_dir.name}'"
        )
    if meta.get("version") and not SEMVER_RE.match(str(meta["version"])):
        errors.append(f"{rel}/package.yml: metadata.version '{meta['version']}' is not MAJOR.MINOR.PATCH")

    spec = doc.get("spec")
    if not isinstance(spec, dict):
        errors.append(f"{rel}/package.yml: spec missing or not a mapping")
        spec = {}
    for field in ("category", "severity", "telemetry", "targets"):
        if not spec.get(field):
            errors.append(f"{rel}/package.yml: spec.{field} is required")

    rules = spec.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append(f"{rel}/package.yml: spec.rules must be a non-empty list")
        rules = []
    for entry in rules:
        if not isinstance(entry, dict) or "path" not in entry or "id" not in entry:
            errors.append(f"{rel}/package.yml: each spec.rules entry needs path + id")
            continue
        rid = str(entry["id"])
        if not UUID_RE.match(rid):
            errors.append(f"{rel}/package.yml: rule id '{rid}' is not a UUID")
        if rid in seen_rule_ids:
            errors.append(f"{rel}/package.yml: rule id '{rid}' already used in {seen_rule_ids[rid]}")
        else:
            seen_rule_ids[rid] = str(rel)
        rule_path = pkg_dir / entry["path"]
        if not rule_path.is_file():
            errors.append(f"{rel}/package.yml: rule file not found: {entry['path']}")
            continue
        rule = load_yaml(rule_path, errors)
        if not isinstance(rule, dict):
            if rule is not None:
                errors.append(f"{rule_path.relative_to(ROOT)}: top level must be a mapping")
            continue
        for field in RULE_REQUIRED:
            if field not in rule or rule[field] in (None, ""):
                errors.append(f"{rule_path.relative_to(ROOT)}: missing required field '{field}'")
        if str(rule.get("id")) != rid:
            errors.append(
                f"{rule_path.relative_to(ROOT)}: id '{rule.get('id')}' does not match manifest id '{rid}'"
            )
        detection = rule.get("detection")
        if isinstance(detection, dict):
            if "condition" not in detection:
                errors.append(f"{rule_path.relative_to(ROOT)}: detection.condition is required")
        elif detection is not None:
            errors.append(f"{rule_path.relative_to(ROOT)}: detection must be a mapping")

    # Every rule file on disk must be listed in the manifest.
    listed = {str((pkg_dir / e["path"]).resolve()) for e in rules if isinstance(e, dict) and "path" in e}
    for rule_file in sorted((pkg_dir / "rules").glob("*.yml")) if (pkg_dir / "rules").is_dir() else []:
        if str(rule_file.resolve()) not in listed:
            errors.append(f"{rel}: rule file {rule_file.name} exists on disk but is not listed in package.yml")

    integrity = doc.get("integrity")
    if not isinstance(integrity, dict) or not SHA256_RE.match(str(integrity.get("contentHash", ""))):
        errors.append(f"{rel}/package.yml: integrity.contentHash must be 'sha256:<64 hex chars>'")


def main() -> int:
    if not EXAMPLES.is_dir():
        print(f"ERROR: examples directory not found at {EXAMPLES}", file=sys.stderr)
        return 2
    pkg_dirs = sorted(p for p in EXAMPLES.iterdir() if p.is_dir())
    if not pkg_dirs:
        print("ERROR: no example packages found under examples/", file=sys.stderr)
        return 2

    errors: list[str] = []
    seen_rule_ids: dict[str, str] = {}
    for pkg_dir in pkg_dirs:
        validate_package(pkg_dir, errors, seen_rule_ids)

    if errors:
        print(f"FAIL: {len(errors)} problem(s) across {len(pkg_dirs)} package(s):\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {len(pkg_dirs)} example package(s) validated ({len(seen_rule_ids)} rules).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
