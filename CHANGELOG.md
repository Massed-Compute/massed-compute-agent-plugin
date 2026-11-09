# CHANGELOG

## 1.0.2 — public directory draft

- Add a separate Claude public management package at `plugins/massed-compute-directory`, using the audience-restricted directory MCP endpoint.
- Adapt the existing-VM inspection and confirmed-change skills from the OpenAI public review work.
- Add explicit privacy metadata, package-local documentation, icon and license.
- Start the public package enabled after explicit installation; provider OAuth and tool permissions still govern account access. The legacy full connector remains disabled by default.
- Document the corrected submission path, data-transmission disclosure, dedicated reviewer account, five positive and three negative tests, and Claude-specific verification limits.
- Preserve the original full connector and Cursor package.

## Unreleased

- Cursor marketplace manifests alongside the existing Claude plugin manifests.
- Cursor `mcp.json` pointing at the same Massed Compute HTTP MCP endpoint without bundled credentials.
- Structural validation for both Claude and Cursor package layouts.
- GitHub Actions pack validation (JSON, structure, secret scan, home-path scan). No OAuth or MCP calls in CI.
- Change-control files: CODEOWNERS, PR template, SECURITY, CONTRIBUTING. Repository stays private.
- Authenticated plugin-qualified read-only smoke completed with no account identifiers recorded and no mutation tools allowed.

## 1.0.0

- Claude Code / Cowork plugin: remote HTTP MCP (`type: http`, OAuth, no bundled Bearer)
- Skills: `setup`, `mc-pick-gpu`, `mc-launch-vms`, `mc-cost-control`, `mc-safe-terminate`
- Ships `defaultEnabled: false`
- Community marketplace submit blocked until this repo is public and an org admin reviews
