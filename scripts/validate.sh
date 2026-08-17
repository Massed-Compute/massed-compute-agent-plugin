#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
claude plugin validate ./plugins/massed-compute --strict
claude plugin validate . --strict
python3 -m json.tool ./plugins/massed-compute/.mcp.json >/dev/null
python3 -m json.tool ./plugins/massed-compute/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool ./.claude-plugin/marketplace.json >/dev/null
echo "validate ok"
