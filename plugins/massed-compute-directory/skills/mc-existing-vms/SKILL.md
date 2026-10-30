---
name: mc-existing-vms
description: Inspect existing Massed Compute VMs, configuration and image information, and SSH public keys. Use when the user asks to validate a Massed Compute connection, list existing VMs, inspect a VM, or view account SSH public keys without changing resources.
---

Use the connected account and this plugin's Massed Compute directory tools.

1. Validate the connection with account_token_validation when needed. Report the actual result without exposing tokens or inventing account identity.
2. Call instances_list for the actual current instance list. Call instances_get only with an actual UUID returned by that list or explicitly supplied by the user. If no instances exist, say so and stop instance-detail inspection.
3. Call gpu_inventory_list and images_list for current reference information. Do not turn reference data into a paid provisioning workflow.
4. Call ssh_keys_list to inspect SSH public keys. An empty list is valid.
5. Report only returned facts. Do not invent a balance, instance, SKU, image, success or error. Redact authentication secrets, instance passwords and unnecessary private connection details.

This public plugin manages existing resources. VM rental or creation, billing changes, coupons, provisioning recipes, SSH execution and software installation are outside its scope. Do not switch to another connector, execute HTTP or shell workarounds, or redirect the user into checkout to perform an unavailable operation.

Authentication belongs in the provider's OAuth flow. Never request passwords, tokens, API keys or private SSH keys in chat. If authentication fails, report the exact safe error and direct the user to reconnect through Claude's connection controls. Never silently fall back to a different account or server.

Read-only instructions authorize no VM or SSH-key changes. Before any requested change, apply mc-safe-changes.
