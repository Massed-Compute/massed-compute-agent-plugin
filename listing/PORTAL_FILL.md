# Marketplace submit fill sheet

Use after an org admin reviews this pack **and** the GitHub repo is public. Do not submit while the repo is private.

Claude form: https://platform.claude.com/plugins/submit  
Cursor form: https://cursor.com/marketplace/publish

Claude requires Console Developer, Admin, or Owner. Cursor requires a signed-in Cursor publisher account.

## Fields

| Field | Value |
| --- | --- |
| GitHub URL | https://github.com/Massed-Compute/massed-compute-agent-plugin |
| Plugin name | massed-compute |
| Display name | Massed Compute |
| Short description | Launch and manage on-demand NVIDIA GPU VMs from chat. |
| Homepage | https://vm-docs.massedcompute.com/docs/mcp/overview |
| Website | https://massedcompute.com/ |
| Support | https://massedcompute.com/contact/ |
| Privacy | https://massedcompute.com/legal/privacy-policy/ |
| Terms | https://massedcompute.com/legal/terms-conditions/ |
| Docs | https://vm-docs.massedcompute.com/docs/mcp/overview |

## Long description (paste)

Official Massed Compute plugin for Claude Code and Cowork. Includes agent skills for picking GPUs, launching VMs, cost control, and safe termination, plus a remote MCP server for live inventory, billing, SSH keys, recipes, and instance lifecycle on your Massed Compute account.

Users authenticate with Massed Compute OAuth (dynamic client registration). Does not sell plans or credits inside chat — billing stays on massedcompute.com. Destructive actions (terminate, SSH key delete) require confirmation.

## MCP

- URL: `https://vm.massedcompute.com/api/mcp`
- Claude file: `plugins/massed-compute/.mcp.json`
- Cursor file: `plugins/massed-compute/mcp.json`
- Transport: HTTP (`type: http`)
- Auth: OAuth 2.1 + PKCE + DCR (no bundled Bearer header)
- Fallback (not for listing): user-supplied `Authorization: Bearer <your-api-key>` from vm.massedcompute.com/settings/api

## Cursor publisher application fields

| Field | Value |
| --- | --- |
| Organization name | Massed Compute |
| Organization handle | massed-compute |
| Contact email | gabe@massedcompute.com |
| Logotype URL | https://massedcompute.com/favicon.ico |
| Description | Launch and manage on-demand NVIDIA GPU VMs from Cursor with Massed Compute MCP and agent skills. |
| GitHub repository | https://github.com/Massed-Compute/massed-compute-agent-plugin |
| Website URL | https://massedcompute.com/ |

## After submit

Do not re-submit the form for updates. Push to this repo; Anthropic CI re-screens and bumps the pin in `anthropics/claude-plugins-community`. Catalog sync can lag a day. Confirm installability by searching `massed-compute` in:

https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json

Install (after pin):

```
/plugin marketplace add anthropics/claude-plugins-community
/plugin install massed-compute@claude-community
```

## Publish gate

Do not click Submit until:

1. This repo is **public** (authorized person only)
2. `claude plugin validate ./plugins/massed-compute --strict` passes locally
3. An org admin has reviewed the pack
4. `tests/SMOKE_CHECKLIST.md` pre + positive items are checked by a human (not CI)
5. Legal attestations and any reviewer-account credentials are completed by that human

OpenAI Plugins Directory is a **different** repository/pack and a separate publish gate. Do not treat Anthropic or Cursor submit as OpenAI approval, or the reverse.

This form does not claim that GitHub Actions completed OAuth or positive MCP calls.
