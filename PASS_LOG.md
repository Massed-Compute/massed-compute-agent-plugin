# Pass log

Share-safe. No secrets, live IDs, or machine paths.

**Scope:** Claude plugin pack (`plugins/massed-compute/`, `README.md`, `listing/`, `tests/`, `scripts/`)
**Type:** docs/skill + manifests
**Done means:** validate-clean, OAuth install path accurate, share-safe for a later public flip
**Out of scope:** Connectors Directory, Submit, making the GitHub repo public

### Pass 1 — Correctness
- **Checked:** manifests, install/OAuth vs live CLI, skill cross-links, leftover OpenAI copy
- **Fixed:** dead `*.md` skill links; ChatGPT/Codex wording; plugin MCP name + `claude mcp login`; `<your-api-key>`; billing URL
- **Verified:** `claude plugin validate ./plugins/massed-compute --strict` and marketplace `--strict`
- **Open:** plugin HTTP OAuth consent requires an interactive terminal

### Pass 2 — Clarity
- **Checked:** README auth vs stdio gateway name collision; skill see-also lists
- **Fixed:** documented `plugin:massed-compute:massed-compute` vs user-level `massed-compute`; launch see-also includes `setup`
- **Verified:** re-read README Auth + Local test
- **Open:** none

### Improve
- **Fixed:** README troubleshooting table (disabled by default, Needs authentication, TTY, name collision)
- **Tradeoffs:**
  - Kept marketplace + `plugins/massed-compute/` layout so testers can `marketplace add .` (vs flattening to plugin-at-root)
  - Kept GPU lineup tables in `mc-pick-gpu` (counselor skill) vs live-inventory-only
  - Did not add `userConfig` API-key prompt; listing default stays OAuth (DCR works; TTY is the blocker)
- **Verified:** troubleshooting rows match `claude plugin install` / `claude mcp get` output

### Pass 3 — Regressions & boundaries
- **Checked:** re-validate; `claude plugin details`; MCP get; grep for leftover OpenAI links
- **Fixed:** none this pass
- **Verified:** 5 skills + 1 MCP in details; HTTP URL correct; `--strict` still green
- **Open:** OAuth still Needs authentication until a human runs `claude mcp login` in a TTY

### Pass 4 — Tests / config
- **Checked:** no unit test runner (markdown plugin)
- **Fixed:** `tests/SMOKE_CHECKLIST.md`; `scripts/validate.sh`
- **Verified:** `./scripts/validate.sh`
- **Open:** positive MCP calls on the plugin HTTP server wait on TTY OAuth

### Pass 5 — Copy
- **Checked:** README, setup skill, portal fill
- **Fixed:** portal fill requires smoke pre+positive; README local test uses `./scripts/validate.sh`
- **Verified:** layout block lists new files
- **Open:** none

### Pass S1 — AuthN / AuthZ
- **Checked:** `defaultEnabled: false`; no bundled credentials; destructive skills gated; setup forbids terminate
- **Fixed:** Bearer fallback server name `massed-compute-bearer` so it cannot clobber the plugin or stdio gateway
- **Verified:** setup skill fallback command
- **Open:** none

### Pass S2 — Input / output
- **Checked:** MCP URL hardcoded `https://`; skills forbid invented JSON fields (`-32602`); no local command MCP
- **Fixed:** none
- **Verified:** `.mcp.json` has `type: http` and no headers
- **Open:** none (server-side validation lives on the hosted MCP, not this pack)

### Pass S3 — Secrets / data
- **Checked:** secret-shaped patterns, emails, home paths on tracked files
- **Fixed:** already using `<your-api-key>` (no live values found)
- **Verified:** grep clean of key-shaped literals and home paths
- **Open:** none

### Pass S4 — Exposure / deps
- **Checked:** no npm/pip lockfile; no debug flags; GitHub repo remains private
- **Fixed:** none
- **Verified:** `scripts/validate.sh`; repo visibility not changed
- **Open:** none

### Finalize
- **Checked:** README install, LICENSE, CHANGELOG, smoke checklist, share-safe logs
- **Fixed:** `CHANGELOG.md`; this log
- **Verified:** `./scripts/validate.sh`
- **Open:** interactive `claude mcp login plugin:massed-compute:massed-compute` then `tests/SMOKE_CHECKLIST.md` positives; public flip + Console submit still gated

### Pass C1 — Change-control / CI (2026-08-17)
- **Checked:** no GitHub Actions on the pack; OAuth still human-owned
- **Fixed:** `.github/workflows/plugin-ci.yml` (SHA-pinned checkout, `contents: read`); `scripts/ci_checks.py`; CODEOWNERS / PR template / SECURITY / CONTRIBUTING / change-control
- **Verified:** `python3 scripts/ci_checks.py` and `./scripts/validate.sh` (CI-safe). Authenticated MCP calls were **not** run in CI and are **not** claimed here.
- **Open:** administrator applies `main` ruleset; independent review of PR; interactive OAuth smoke; keep repo private; no marketplace submit

