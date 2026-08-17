# Massed Compute — Claude Code plugin

Official plugin for [Claude Code](https://code.claude.com) and Cowork: remote Massed Compute MCP plus skills for GPU pick, launch, cost control, and safe terminate.

This is **not** a Claude Connectors Directory listing. Connectors (Claude.ai / Desktop / mobile) are a separate portal.

## Status: private draft

This repository is **private on purpose**. Anthropic's community marketplace **rejects closed-source plugins**. Do not submit until:

1. An org admin has reviewed this pack
2. This GitHub repo is flipped **public**
3. Someone with Console Developer / Admin / Owner submits at [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

Do not click Submit, Publish, or make the repo public without that go-ahead.

## Layout

```
.claude-plugin/marketplace.json     # self-serve marketplace while testing
plugins/massed-compute/
  .claude-plugin/plugin.json
  .mcp.json                         # HTTP MCP, OAuth (no Bearer header)
  skills/mc-pick-gpu/
  skills/mc-launch-vms/
  skills/mc-cost-control/
  skills/mc-safe-terminate/
  skills/setup/
listing/PORTAL_FILL.md              # Console form copy
```

## Auth

MCP URL: `https://vm.massedcompute.com/api/mcp`

Claude Code starts OAuth (DCR + PKCE) because `.mcp.json` has `type: http` and **no** `Authorization` header. Consent offers full access or read-only. Bearer API keys remain a documented fallback in `skills/setup/SKILL.md` — they are not bundled.

The plugin ships `defaultEnabled: false`. Enable it after install; it talks to a paid account.

## Local test (private repo)

From this repo:

```bash
claude plugin validate ./plugins/massed-compute
claude --plugin-dir ./plugins/massed-compute
```

Inside Claude Code:

```
/plugin marketplace add /absolute/path/to/massed-compute-claude-plugin
/plugin install massed-compute@massed-compute
```

Then enable the plugin, run `/mcp`, complete OAuth, and call a read tool (e.g. validate token / list inventory).

GitHub-org teammates with repo access can add `Massed-Compute/massed-compute-claude-plugin` the same way once they can clone.

## After it is public + approved

```
/plugin marketplace add anthropics/claude-plugins-community
/plugin install massed-compute@claude-community
```

Anthropic pins a commit SHA and syncs the catalog nightly. Later updates: push here; do not re-submit the form.

## Submit plan (blocked)

1. Review pack (this README, `plugins/massed-compute`, `listing/PORTAL_FILL.md`)
2. Flip GitHub visibility to public
3. Fill [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit) from `listing/PORTAL_FILL.md`
4. Wait for automated `claude plugin validate` + safety screen
5. Confirm `massed-compute` appears in [claude-plugins-community marketplace.json](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json)

Out of scope: Connectors Directory, `claude-plugins-official` (invite-only).

## Links

- Docs: https://vm-docs.massedcompute.com/docs/mcp/overview
- Privacy: https://massedcompute.com/legal/privacy-policy/
- Terms: https://massedcompute.com/legal/terms-conditions/
- Support: https://massedcompute.com/contact/
