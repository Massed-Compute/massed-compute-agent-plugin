#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

python3 "$root/scripts/ci_checks.py"

if command -v claude >/dev/null 2>&1; then
  claude plugin validate ./plugins/massed-compute --strict
  claude plugin validate . --strict
else
  echo "claude CLI not installed; skipped claude plugin validate --strict"
  echo "CI structural JSON/skill/secret/path checks still ran."
  echo "Authorized reviewers run claude plugin validate locally; see tests/SMOKE_CHECKLIST.md"
fi

echo "validate ok"
