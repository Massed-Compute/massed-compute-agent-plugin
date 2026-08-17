# Change control

Related ticket: MAR-19 (Claude / marketplace listing). Do not submit or change repository visibility from this branch.

This file does not by itself establish SOC 2 compliance.

## PR checklist

- [ ] Feature branch only
- [ ] Ticket link
- [ ] `./scripts/validate.sh` recorded
- [ ] No secrets / home paths
- [ ] Independent reviewer named
- [ ] Interactive OAuth listed as human follow-up unless already completed off-CI

## Rollback

Plugin pack is not auto-deployed. Rollback = revert merge via a new PR.
If testers installed a bad pack: disable the plugin, remove the local marketplace, reinstall from a known-good commit.
Never force-push `main`.

## What CI does not do

CI does not log into Massed Compute, does not complete OAuth, and does not prove positive MCP tool calls.
