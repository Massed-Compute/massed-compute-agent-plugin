---
name: mc-safe-changes
description: Guide explicitly confirmed changes to existing Massed Compute VMs and SSH public keys. Use before restarting or terminating a VM or adding or deleting an account SSH public key, including requests to delete all VMs or skip confirmation.
---

Operate only on the connected account and the user's specific intended resources.

For VM restart or termination, first inspect instances_list or instances_get. Show the exact UUID, name, configuration and consequence. Restart interrupts work. Termination permanently deletes the selected instance and its data. Honor user protection lists and never infer that all instances are disposable. If a protection registry is supplied in the environment, read it before a destructive action and honor it. Do not create a VM to test this workflow.

For SSH-key deletion, inspect ssh_keys_list and disclose the exact key and possible loss of access. For addition, accept only a public SSH key and the requested label. Never request or use a private key, and never repeat private key material supplied accidentally.

Before a destructive change, obtain explicit confirmation after disclosing the exact affected resources and consequences. A vague request such as "kill all" or a request to skip confirmation does not replace that disclosure. If nothing matches, report that and do not call a write tool. If a user has prohibited resource changes, stop before any write even when a confirmation would otherwise be possible.

Call only the confirmed operation for the confirmed identifiers. Do not evade a read-only grant or permission denial by changing credentials, servers or transport. After a permitted write, inspect the resulting state with a read tool and report the actual outcome. Report precise safe API errors instead of claiming success.

VM creation/rental, billing, coupons and provisioning are outside this public plugin. Read-only review tests authorize no writes.
