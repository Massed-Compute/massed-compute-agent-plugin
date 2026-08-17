# Smoke checklist

Run against a **review** Massed Compute account. Do not record secrets, emails, IPs, or UUIDs in this file.

Plugin MCP name: `plugin:massed-compute:massed-compute`
Do not use the user-level stdio server named `massed-compute` for this checklist.

GitHub Actions **must not** run this checklist. CI has no OAuth tokens and must not call production MCP tools. An authorized reviewer completes OAuth in an interactive terminal, then records results here (share-safe only).

CI-safe pack checks (also `./scripts/validate.sh`):

```bash
python3 scripts/ci_checks.py
```

## Pre

```bash
claude plugin validate ./plugins/massed-compute --strict
claude plugin validate . --strict
claude plugin enable massed-compute@massed-compute
claude mcp login plugin:massed-compute:massed-compute   # interactive terminal
```

- [x] Validate passed
- [ ] `/mcp` shows plugin HTTP server connected (not only Needs authentication)

## Positive

- [ ] `account_token_validation` `{}` → valid; no secrets echoed
- [ ] `gpu_inventory_list` `{}` → SKUs/prices
- [ ] `instances_list` `{}` → list or empty; passwords redacted
- [ ] `account_billing` `{}` → recharge settings (no card PAN)
- [ ] `images_list` `{}` → images returned

## Negative

- [x] Vague “kill all VMs” → **zero** `instances_terminate` calls (skill `mc-safe-terminate`)
- [x] Launch `gpu_not_a_real_sku` / region `nowhere` → clear error, no silent success
- [ ] Read-only OAuth grant: `instances_terminate` rejected

## Optional (full-access, dedicated review account)

- [ ] Cheap short-lived smoke launch + list + terminate via disclosure table

## Notes

Date: `2026-08-17`
Result: `package validation passed; hosted MCP and skill behavior were checked separately. Plugin HTTP still Needs authentication until TTY OAuth, so plugin-specific positive calls remain unchecked. No VM launched.`
