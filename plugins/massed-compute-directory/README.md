# Massed Compute — existing VM management

Connect an existing Massed Compute account to inspect VMs, configuration and image information, and SSH public keys. Restart or permanently terminate specific existing VMs, or manage SSH public keys, only after reviewing the affected resources and confirming the action.

This package exposes the public management endpoint. VM creation/rental, billing changes, coupons, provisioning recipes, SSH execution and software installation are outside its scope.

## Connect and inspect

1. Install the plugin and connect its MCP server. The plugin starts enabled after installation; OAuth and tool permissions still control account access and changes.
2. Connect its remote MCP server through the client's OAuth controls and sign in to your Massed Compute account on the provider's website. No password, API key or token belongs in chat or this package.
3. Ask: "Validate my Massed Compute connection and list my existing VMs without changing anything."
4. An empty VM or SSH-key list is valid. The plugin does not provision a resource to populate an empty account.

Claude Code local testing:

```sh
claude --plugin-dir ./plugins/massed-compute-directory
```

After the reviewed package is available in the repository's marketplace:

```text
/plugin install massed-compute-directory --marketplace Massed-Compute/massed-compute-agent-plugin
```

The local draft must be reviewed and released before this install command can fetch it from GitHub.

Use `/mcp` in that session to connect the plugin's HTTP server. Verify the displayed server belongs to this plugin and uses the endpoint below. A successful call through an unrelated global MCP connection does not verify this package.

## Tools and permissions

Endpoint: `https://vm.massedcompute.com/api/mcp/directory`

Read tools: `account_token_validation`, `instances_list`, `instances_get`, `gpu_inventory_list`, `images_list`, `ssh_keys_list`.

Change tools: `instances_restart`, `instances_terminate`, `ssh_keys_create`, `ssh_keys_delete`. Authentication permissions and explicit user confirmation both apply. Select read-only access when only inspection is intended.

Two skills guide inspection and confirmed changes: `mc-existing-vms` and `mc-safe-changes`. No shell commands, hooks, third-party launchers or bundled credentials execute on installation.

## Data handling

This plugin transmits data to Massed Compute's remote MCP server at `vm.massedcompute.com`. Authorized requests include requested tool names, resource identifiers and parameters, and public SSH-key material only when the user explicitly requests a key addition. Results returned to the client may include account-resource information, VM configuration/status and public-key metadata. The provider handles sign-in and OAuth consent in its own website. Treat OAuth tokens and any secret fields in tool responses as confidential; do not display them in chat.

Do not supply private SSH keys. The package contains no credentials and has no independent analytics or telemetry code. Provider-side processing, retention and account rights are governed by the privacy policy; this package makes no additional retention promise.

- [Privacy policy](https://massedcompute.com/legal/privacy-policy/)
- [Terms](https://massedcompute.com/legal/terms-conditions/)
- [Support](https://massedcompute.com/contact/)
- [MCP documentation](https://vm-docs.massedcompute.com/docs/mcp/overview)

## Review testing limits

Use a dedicated sample account. Start with read-only checks. If it has no VM, instance-detail inspection cannot be demonstrated; do not invent a UUID or launch one. A successful read check does not prove restart, termination or SSH-key mutation. Those operations need separately approved disposable resources and confirmation.

The OpenAI review recording demonstrates a separate client's earlier connection to the same endpoint. It is supporting server evidence and does not demonstrate Claude-specific installation, OAuth or skill routing.
