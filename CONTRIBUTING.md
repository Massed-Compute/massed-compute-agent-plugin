# Contributing

Default branch is `main`. Do not push to `main`. Do not make this repository public from a PR.

## Ticket

Link Jira. Marketplace listing: **MAR-19**.

## Review

Independent approval from someone other than the author. CODEOWNERS: `@Massed-Compute/techadmin` (admin must confirm write access).

## Local checks

```bash
./scripts/validate.sh
```

If Claude CLI is installed, that also runs `claude plugin validate --strict`. CI runs the same script without Claude CLI (structural JSON, skills, secret scan, home-path scan).

## Required CI names (after admin applies branch protection)

- `json-validate`
- `secrets-scan`
- `home-path-scan`
- `plugin-validate`

## Publication

Private install, GitHub visibility, Anthropic community submit, and OpenAI directory submit are **separate** gates. See `README.md` and `listing/PORTAL_FILL.md`. Legal attestations and reviewer credentials are human-owned.

These files support change control. They do not by themselves establish SOC 2 compliance.
