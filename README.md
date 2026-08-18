# Massed Compute — AI agent plugin

Official plugin for [Claude Code](https://code.claude.com), Claude Cowork, and Cursor: remote Massed Compute MCP plus skills for GPU pick, launch, cost control, and safe terminate.

This is **not** a Claude Connectors Directory listing. Connectors (Claude.ai / Desktop / mobile) are a separate portal.

## Status: marketplace review pack

Do not submit to any marketplace from a feature branch.

Separate gates:

1. **Private installation** — clone this repo and install locally while testing.
2. **Repository publication** — an authorized person makes the GitHub repo public.
3. **Claude community marketplace** — Console submit at [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit) using `listing/PORTAL_FILL.md`. Anthropic rejects closed-source plugins. Legal attestations and reviewer credentials are filled by a human, not CI.
4. **Cursor marketplace** — Submit the same GitHub repo at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Cursor reads `.cursor-plugin/marketplace.json`, `plugins/massed-compute/.cursor-plugin/plugin.json`, and `plugins/massed-compute/mcp.json`.
5. **OpenAI Plugins Directory** — different pack and a separate org-admin publish gate. Not this repository.

Do not click Submit, Publish, or make the repo public without that go-ahead.

CI (`plugin-validate`, `json-validate`, `secrets-scan`, `home-path-scan`) never authenticates to Massed Compute and never proves OAuth or positive MCP calls. Those remain `tests/SMOKE_CHECKLIST.md` (interactive TTY).

## Layout

```
.claude-plugin/marketplace.json     # self-serve marketplace while testing
.cursor-plugin/marketplace.json     # Cursor marketplace registry
plugins/massed-compute/
  .claude-plugin/plugin.json
  .cursor-plugin/plugin.json
  .mcp.json                         # HTTP MCP, OAuth (no Bearer header)
  mcp.json                          # Cursor HTTP MCP config, same server
  skills/mc-pick-gpu/
  skills/mc-launch-vms/
  skills/mc-cost-control/
  skills/mc-safe-terminate/
  skills/setup/
listing/PORTAL_FILL.md              # Console form copy
tests/SMOKE_CHECKLIST.md
scripts/validate.sh
CHANGELOG.md
PASS_LOG.md
```

## Auth

MCP URL: `https://vm.massedcompute.com/api/mcp`

Claude Code starts OAuth (DCR + PKCE) because `.mcp.json` has `type: http` and **no** `Authorization` header. Cursor uses `mcp.json` with the same HTTP MCP server and no bundled credentials. Consent offers full access or read-only. Bearer API keys remain a documented fallback in `plugins/massed-compute/skills/setup/SKILL.md` — they are not bundled.

The plugin MCP appears as `plugin:massed-compute:massed-compute`. A user-level stdio server named `massed-compute` (the `massed-compute.mcp` gateway) is a different process — do not treat a successful call on that gateway as plugin OAuth.

The plugin ships `defaultEnabled: false`. Enable it after install; it talks to a paid account.

## Local test (private repo)

From this repo:

```bash
./scripts/validate.sh
claude --plugin-dir ./plugins/massed-compute
```

Install (plugin ships disabled):

```
claude plugin marketplace add .
claude plugin install massed-compute@massed-compute
claude plugin enable massed-compute@massed-compute
```

MCP server name: `plugin:massed-compute:massed-compute`. Authenticate, then call a read tool:

```
claude mcp login plugin:massed-compute:massed-compute
```

Or inside Claude Code: `/plugin marketplace add .` then `/plugin install massed-compute@massed-compute`, enable it, `/mcp`, complete OAuth.

GitHub-org teammates with repo access can add `Massed-Compute/massed-compute-agent-plugin` the same way once they can clone.

## Cursor package

Cursor uses its own manifest wrapper while sharing the same plugin contents:

```
.cursor-plugin/marketplace.json
plugins/massed-compute/.cursor-plugin/plugin.json
plugins/massed-compute/mcp.json
plugins/massed-compute/skills/
```

`plugins/massed-compute/mcp.json` intentionally matches the Claude `.mcp.json` server URL and ships no bearer token or static Authorization header. Users authenticate through Massed Compute OAuth or a user-managed local MCP fallback; credentials are never committed to this repo.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Plugin installed but no MCP | `defaultEnabled` is false. Run `claude plugin enable massed-compute@massed-compute`, then `/reload-plugins`. |
| `/mcp` shows Needs authentication | `claude mcp login plugin:massed-compute:massed-compute` in an **interactive** terminal (browser consent). Non-TTY agents cannot finish OAuth. |
| Token looks valid but you never saw a browser | You likely hit the user-level stdio gateway named `massed-compute`, not `plugin:massed-compute:massed-compute`. |
| `claude mcp login` says stdin isn't a terminal | Re-run in a real terminal, not a piped agent shell. |
| OAuth still failing | Follow `plugins/massed-compute/skills/setup/SKILL.md`. Bearer fallback is last resort and must not be committed. |

## After Claude is public + approved

```
/plugin marketplace add anthropics/claude-plugins-community
/plugin install massed-compute@claude-community
```

Anthropic pins a commit SHA and syncs the catalog nightly. Later updates: push here; do not re-submit the form.

## Submit plan

1. Review pack (this README, `plugins/massed-compute`, `listing/PORTAL_FILL.md`)
2. Flip GitHub visibility to public
3. Fill [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit) from `listing/PORTAL_FILL.md`
4. Fill [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) with the same public GitHub repo
5. Wait for automated validation + marketplace review
6. Confirm `massed-compute` appears in the approved Claude and Cursor marketplace surfaces

Out of scope: Connectors Directory, `claude-plugins-official` (invite-only).

## Links

- Docs: https://vm-docs.massedcompute.com/docs/mcp/overview
- Privacy: https://massedcompute.com/legal/privacy-policy/
- Terms: https://massedcompute.com/legal/terms-conditions/
- Support: https://massedcompute.com/contact/
