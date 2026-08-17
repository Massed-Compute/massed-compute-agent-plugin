---
name: setup
description: Use when the user installs or enables the Massed Compute plugin, MCP tools are missing, OAuth/auth fails, or they ask how to connect a Massed Compute account in Claude Code.
---

# Massed Compute plugin setup

Walk the user through connecting the bundled Massed Compute MCP. Do not invent config. Do not paste API keys into chat, JSON, or git.

## Expected state

After `/plugin install massed-compute@…` (or `--plugin-dir`) and enable:

1. Plugin is **enabled** (it ships `defaultEnabled: false` because it talks to a paid account).
2. `/mcp` lists a `massed-compute` server from this plugin.
3. First tool use opens a **browser OAuth consent** on Massed Compute (full access vs read-only). Claude Code handles DCR + PKCE. No Bearer header is bundled.

## Checklist

1. Confirm the plugin is enabled (`/plugin` → Installed → massed-compute). If it is installed but disabled, enable it.
2. Run `/mcp`. The plugin server must appear. If it does not, `/reload-plugins` once, then retry.
3. Ask the user to complete OAuth in the browser. Consent is account-bound. Recommend **read-only** unless they need launch / restart / terminate / SSH key changes.
4. After consent, call `account_token_validation` (empty args `{}`). Real account data means the connection works.
5. If they want to launch or terminate, confirm the grant is full-access before calling write tools.

## If OAuth fails

Do not invent a workaround config. In order:

1. Retry `/mcp` → disable/enable the plugin server so Claude Code rediscovers `WWW-Authenticate` / `.well-known` metadata.
2. Confirm they can log into [vm.massedcompute.com](https://vm.massedcompute.com) in a browser.
3. **Fallback only:** they may add a Bearer key themselves (not via this plugin's `.mcp.json`):

```
claude mcp add --transport http massed-compute https://vm.massedcompute.com/api/mcp --header "Authorization: Bearer <key>"
```

Key from [vm.massedcompute.com/settings/api](https://vm.massedcompute.com/settings/api). They paste it into their own terminal, not into chat. Read-only key for inspect-only; full-access for lifecycle tools.

4. Docs: https://vm-docs.massedcompute.com/docs/mcp/setup

## Do not

- Put secrets in `plugin.json`, `.mcp.json`, skills, or commits
- Upsell plans or credits in chat — billing stays on massedcompute.com
- Call `instances_terminate` or `ssh_keys_delete` during setup
