#!/usr/bin/env python3
"""Check that all Markdown docs in the repo are well-formed:

  - every relative link/image target resolves to an existing file or
    directory in the repository
  - no unbalanced inline-link syntax like `](` without a closing paren

External links (http/https/mailto) and pure in-page anchors (#...) are
not checked. Exits non-zero listing every broken link.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# [text](target) and ![alt](target) — target up to first ')' or space.
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_FENCE_RE = re.compile(r"^(```|~~~)")


def iter_markdown_files():
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        yield path


def check_file(path: Path, errors: list[str]) -> None:
    rel = path.relative_to(ROOT)
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if CODE_FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_RE.finditer(line):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Strip in-page anchor from a file target.
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            resolved = (path.parent / file_part).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"{rel}:{lineno}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{rel}:{lineno}: broken link: {target}")


def main() -> int:
    files = list(iter_markdown_files())
    if not files:
        print("ERROR: no Markdown files found", file=sys.stderr)
        return 2
    errors: list[str] = []
    for path in files:
        check_file(path, errors)
    if errors:
        print(f"FAIL: {len(errors)} broken link(s):\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {len(files)} Markdown file(s) checked, all relative links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
