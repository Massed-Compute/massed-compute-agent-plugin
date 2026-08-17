> Technical repository controls do not by themselves establish SOC 2 compliance.
> The PR author cannot approve this PR.

## Summary

1-3 sentences: what changes and why.

## Ticket / Work Item

Jira / GitHub issue. Claude marketplace listing work uses **MAR-19** unless a dedicated ticket exists.

-

## Justification

Why now? What problem does this solve, or what risk does it reduce?

## Risk level

Low / Medium / High — and why.

## Security and privacy impact

MCP auth, secrets, marketplace metadata, skills, or none.

## Testing

Command(s) and result(s). GitHub Actions must not run authenticated MCP calls.

- [ ] `./scripts/validate.sh` (CI-safe checks)
- [ ] Interactive OAuth smoke (human-only; `tests/SMOKE_CHECKLIST.md`) — or N/A
- [ ] No tests needed — explain why:

## Screenshots

N/A unless UI copy or marketplace listing screenshots.

## Deployment plan

Private clone / plugin install only, until an authorized person approves making the GitHub repo public. This PR must not publish or submit.

## Rollout / Rollback

- Rollout: merge to `main` after independent approval; no marketplace submit from this PR.
- Rollback: revert the merge commit on a new PR; do not force-push `main`. If a bad plugin pack reached testers, tell them to disable `massed-compute@massed-compute` and reinstall a prior commit.

## Required non-author reviewer

Name or team. Author cannot approve.

## Follow-up work / documented exceptions

Open items (OAuth smoke, publication gates) or "none".

---

## Reviewer Checklist

The authorized reviewer confirms, before approving, that:

- [ ] Description, ticket, and justification are sufficient without asking the author.
- [ ] CI `plugin-validate` / `json-validate` / `secrets-scan` / `home-path-scan` were considered; failures were not bypassed.
- [ ] Pack remains free of secrets, live tokens, and machine-specific home paths.
- [ ] No request to make the repository public or submit to a marketplace is implied by this PR.
