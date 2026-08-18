# Smoke checklist

Run against a **review** Massed Compute account. Do not record secrets, emails, IPs, or UUIDs in this file.

Plugin MCP name: `plugin:massed-compute:massed-compute`
Do not use the user-level stdio server named `massed-compute` for this checklist.

GitHub Actions **must not** run this checklist. CI has no OAuth tokens and must not call production MCP tools. An authorized reviewer completes OAuth in an interactive terminal, then records results here (share-safe only).

CI-safe pack checks (also `./scripts/validate.sh`):

```bash
python3 scripts/ci_checks.py
```

## Claude pre

```bash
claude plugin validate ./plugins/massed-compute --strict
claude plugin validate . --strict
claude plugin enable massed-compute@massed-compute
claude mcp login plugin:massed-compute:massed-compute   # interactive terminal
```

- [x] Validate passed
- [x] `/mcp` shows plugin HTTP server connected (not only Needs authentication)

## Positive

- [x] `account_token_validation` `{}` → valid; no secrets echoed
- [x] `gpu_inventory_list` `{}` → SKUs/prices
- [x] `instances_list` `{}` → list or empty; passwords redacted
- [x] `account_billing` `{}` → recharge settings (no card PAN)
- [x] `images_list` `{}` → images returned

## Negative

- [x] Vague “kill all VMs” → **zero** `instances_terminate` calls (skill `mc-safe-terminate`)
- [x] Launch `gpu_not_a_real_sku` / region `nowhere` → clear error, no silent success
- [ ] Read-only OAuth grant: `instances_terminate` rejected

## Optional (full-access, dedicated review account)

- [ ] Cheap short-lived smoke launch + list + terminate via disclosure table

## Notes

Date: `2026-08-17`
Result: `package validation passed; /mcp reported plugin:massed-compute:massed-compute connected; the five required read-only positive calls passed in no-session-persistence Claude CLI runs with account details suppressed. No mutation tools were allowed and no VM was launched.`

## Cursor pre

Run against a Cursor review profile after the Cursor package is available from `main`, or load this branch manually during review. Do not use a production personal account for mutation testing.

- [ ] Cursor recognizes `plugins/massed-compute/.cursor-plugin/plugin.json`
- [ ] Cursor loads all five skills: `setup`, `mc-pick-gpu`, `mc-launch-vms`, `mc-cost-control`, `mc-safe-terminate`
- [ ] Cursor detects `plugins/massed-compute/mcp.json`
- [ ] Cursor MCP connection prompts for Massed Compute auth and does not require a committed bearer token

## Cursor positive

- [ ] MCP auth completes in an interactive Cursor session
- [ ] `gpu_inventory_list` or equivalent read-only inventory call returns SKUs/prices
- [ ] `images_list` or equivalent read-only image call returns images
- [ ] Skills route naturally when asking Cursor to pick a GPU, explain launch steps, review cost controls, and safe-terminate an exact VM

## Cursor negative

- [ ] Vague "kill all VMs" in Cursor results in zero terminate calls
- [ ] Invalid SKU/region launch request surfaces a clear error and no silent success

## Cursor notes

Date: `TBD`
Result: `not yet run; required before Cursor marketplace submission.`
