# Security

Report vulnerabilities through https://massedcompute.com/contact/ .
Do not file public issues for secrets or auth issues. This repository must stay **private** until an authorized person approves publication.

## Auth

Bundled MCP config is HTTP + OAuth (DCR + PKCE). Do not add an `Authorization` header to `.mcp.json`.
Bearer keys are a documented fallback placeholder (`<your-api-key>`) only.

## CI

GitHub Actions in this repo must not receive OAuth tokens or API keys and must not call production MCP tools. CI combines repository-wide literal checks with a checksum-verified Gitleaks history scan.
Interactive OAuth smoke is human-owned (`tests/SMOKE_CHECKLIST.md`).
