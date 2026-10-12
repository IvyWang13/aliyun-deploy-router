#!/usr/bin/env python3
"""Check this skill's required files, including broken or cyclic symlinks."""
import argparse
import json
from pathlib import Path

REQUIRED = (
    'SKILL.md', 'agents/openai.yaml', 'references/routes.md',
    'references/issue-repair.md', 'references/known-issues.md',
    'scripts/search_issues.py', 'scripts/check_install.py',
)


def check(root):
    failures = []
    for name in REQUIRED:
        try:
            path = (root / name).resolve(strict=True)
            if not path.is_file() or not path.read_text(encoding='utf-8').strip():
                failures.append({'file': name, 'reason': 'not a nonempty readable text file'})
        except (OSError, RuntimeError, UnicodeError) as error:
            failures.append({'file': name, 'reason': type(error).__name__})
    return {'ok': not failures, 'checked_files': len(REQUIRED), 'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).absolute().parent.parent)
    args = parser.parse_args()
    result = check(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
